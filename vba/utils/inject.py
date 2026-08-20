"""Inject VBA macros into Office Open XML documents.

Builds vbaProject.bin (OLE2) from scratch with no PerformanceCache.
Sets _VBA_PROJECT version to a known Office version so Word recompiles
p-code from source on first open.
"""

from __future__ import annotations

import io
import math
import struct
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import olefile
from docx import Document as WordDocument
from lxml import etree

from vba.utils.vbaproject import _vba_compress_verified

# _VBA_PROJECT version — must be a known Office version, not 0x0000
_VBA_PROJECT_VERSION = 0x00B5  # Office 2016


# ---------------------------------------------------------------------------
# VBA stream assembly
# ---------------------------------------------------------------------------

class VBAProject:
    """Assembles all OLE2 streams for a VBA project."""

    def __init__(self, macro_code: str):
        self.macro_code = macro_code

    def build_streams(self) -> dict[str, bytes]:
        return {
            'VBA/NewMacros': self._new_macros(),
            'VBA/ThisDocument': self._this_document(),
            'VBA/_VBA_PROJECT': self._vba_project_stream(),
            'VBA/dir': self._dir_stream(),
            'PROJECT': self._project_stream(),
            'PROJECTwm': self._projectwm_stream(),
        }

    def _new_macros(self) -> bytes:
        source = 'Attribute VB_Name = "NewMacros"\r\n' + self.macro_code
        try:
            raw = source.encode('ascii')
        except UnicodeEncodeError as e:
            raise ValueError(
                f'Macro contains non-ASCII character at position {e.start}. '
                f'VBA source must be pure ASCII.'
            ) from None
        return _vba_compress_verified(raw)

    def _this_document(self) -> bytes:
        source = (
            'Attribute VB_Name = "ThisDocument"\r\n'
            'Attribute VB_Base = "1Normal.ThisDocument"\r\n'
            'Attribute VB_GlobalNameSpace = False\r\n'
            'Attribute VB_Creatable = False\r\n'
            'Attribute VB_PredeclaredId = True\r\n'
            'Attribute VB_Exposed = True\r\n'
            'Attribute VB_TemplateDerived = True\r\n'
            'Attribute VB_Customizable = True\r\n'
        )
        return _vba_compress_verified(source.encode('ascii'))

    def _vba_project_stream(self) -> bytes:
        return struct.pack('<HHBH', 0x61CC, _VBA_PROJECT_VERSION, 0x00, 0x0000)

    def _dir_stream(self) -> bytes:
        d = bytearray()
        rec = _rec

        # Project information
        d += rec(0x0001, struct.pack('<I', 3))       # SysKind Win64
        d += rec(0x0002, struct.pack('<I', 0x0409))  # LCID
        d += rec(0x0014, struct.pack('<I', 0x0409))  # LCIDInvoke
        d += rec(0x0003, struct.pack('<H', 1252))    # CodePage
        d += rec(0x0004, b'Project')                 # Name
        d += rec(0x0005, b'')                        # DocString
        d += rec(0x0040, b'')                        # DocStringUnicode
        d += rec(0x0006, b'')                        # HelpFile1
        d += rec(0x003D, b'')                        # HelpFile2
        d += rec(0x0007, struct.pack('<I', 0))       # HelpContext
        d += rec(0x0008, struct.pack('<I', 0))       # LibFlags
        d += struct.pack('<HIIH', 0x0009, 4, 1, 1)  # Version
        d += rec(0x000C, b'')                        # Constants
        d += rec(0x003C, b'')                        # ConstantsUnicode

        # References
        for name, libid in _REFERENCES:
            name_u = name.encode('utf-16-le')
            d += rec(0x0016, name.encode('ascii'))
            d += struct.pack('<HI', 0x003E, len(name_u))
            d += name_u
            d += rec(0x000D, struct.pack('<I', len(libid)) + libid + b'\x00' * 6)

        # Modules
        d += struct.pack('<HIH', 0x000F, 2, 2)       # Count=2
        d += struct.pack('<HIH', 0x0013, 2, 0xFFFF)  # Cookie

        for mod in _MODULES:
            name_a = mod.name.encode('ascii')
            name_u = mod.name.encode('utf-16-le')
            d += rec(0x0019, name_a)
            d += rec(0x0047, name_u)
            d += rec(0x001A, name_a)
            d += rec(0x0032, name_u)
            d += rec(0x001C, b'')
            d += rec(0x0048, b'')
            d += rec(0x0031, struct.pack('<I', 0))    # TextOffset=0
            d += rec(0x001E, struct.pack('<I', 0))
            d += rec(0x002C, struct.pack('<H', 0xFFFF))
            d += rec(mod.type_id)
            d += struct.pack('<HI', 0x002B, 0)

        d += struct.pack('<HI', 0x0010, 0)  # Dir terminator
        return _vba_compress_verified(bytes(d))

    def _project_stream(self) -> bytes:
        text = (
            'ID="{00000000-0000-0000-0000-000000000000}"\r\n'
            'Document=ThisDocument/&H00000000\r\n'
            'Module=NewMacros\r\n'
            'Name="Project"\r\n'
            'HelpContextID="0"\r\n'
            'VersionCompatible32="393222000"\r\n'
            'CMG=""\r\n'
            'DPB=""\r\n'
            'GC=""\r\n'
            '\r\n'
            '[Host Extender Info]\r\n'
            '&H00000001={3832D640-CF90-11CF-8E43-00A0C911005A};VBE;&H00000000\r\n'
            '\r\n'
            '[Workspace]\r\n'
            'ThisDocument=0, 0, 0, 0, C\r\n'
            'NewMacros=0, 0, 0, 0, C\r\n'
        )
        return text.encode('ascii')

    def _projectwm_stream(self) -> bytes:
        out = bytearray()
        for mod in _MODULES:
            out += mod.name.encode('ascii') + b'\x00'
            out += mod.name.encode('utf-16-le') + b'\x00\x00'
        out += b'\x00\x00'
        return bytes(out)


def _rec(rid: int, data: bytes = b'') -> bytes:
    """Build a VBA dir stream record: 2-byte id + 4-byte length + data."""
    return struct.pack('<HI', rid, len(data)) + data


@dataclass
class ModuleDecl:
    """VBA module declaration for the dir stream."""
    name: str
    type_id: int  # 0x0021=procedural, 0x0022=document


_MODULES = [
    ModuleDecl('ThisDocument', 0x0022),
    ModuleDecl('NewMacros', 0x0021),
]

_REFERENCES = [
    (
        'stdole',
        b'*\\G{00020430-0000-0000-C000-000000000046}#2.0#0#C:\\Windows\\System32\\stdole2.tlb#OLE Automation',
    ),
    (
        'Office',
        b'*\\G{2DF8D04C-5BFA-101B-BDE5-00AA0044DE52}#2.0#0#C:\\Program Files\\Common Files\\Microsoft Shared\\OFFICE16\\MSO.DLL#Microsoft Office 16.0 Object Library',
    ),
]


# ---------------------------------------------------------------------------
# OLE2 compound file builder
# ---------------------------------------------------------------------------

_ENDOFCHAIN = 0xFFFFFFFE
_FREESECT = 0xFFFFFFFF
_FATSECT = 0xFFFFFFFD
_NOSTREAM = 0xFFFFFFFF
_SECTOR_SIZE = 512
_MINI_SECTOR_SIZE = 64
_MINI_CUTOFF = 4096
_FAT_PER_SECTOR = _SECTOR_SIZE // 4


@dataclass
class _StreamInfo:
    """Tracks where a stream is placed in the OLE2 file."""
    start_sector: int = 0
    size: int = 0
    mini: bool = True  # True = mini stream, False = regular sectors


class OLE2Builder:
    """Builds an OLE2 compound file from named streams."""

    # Stream order and directory tree layout (hardcoded for VBA project)
    _STREAM_ORDER = [
        ('VBA/ThisDocument', 'ThisDocument'),
        ('VBA/NewMacros', 'NewMacros'),
        ('VBA/_VBA_PROJECT', '_VBA_PROJECT'),
        ('VBA/dir', 'dir'),
        ('PROJECTwm', 'PROJECTwm'),
        ('PROJECT', 'PROJECT'),
    ]

    def __init__(self, streams: dict[str, bytes]):
        self._streams = streams
        self._info: dict[str, _StreamInfo] = {}

    def build(self) -> bytes:
        small = [(p, n) for p, n in self._STREAM_ORDER if len(self._streams[p]) < _MINI_CUTOFF]
        large = [(p, n) for p, n in self._STREAM_ORDER if len(self._streams[p]) >= _MINI_CUTOFF]

        mini_stream, ms_logical = self._build_mini_stream(small)
        mini_fat = self._build_mini_fat(small)
        large_blobs = self._pad_large_streams(large)

        ms_sectors = len(mini_stream) // _SECTOR_SIZE if mini_stream else 0
        mfat_sectors = max(1, math.ceil(len(mini_fat) / _SECTOR_SIZE))
        large_total = sum(len(b) // _SECTOR_SIZE for b in large_blobs.values())
        dir_sectors = 2

        fat_sectors = self._compute_fat_sectors(dir_sectors, mfat_sectors, ms_sectors, large_total)

        # Sector layout: [FAT] [DIR] [MFAT] [MS] [LARGE...]
        fat_start = 0
        dir_start = fat_start + fat_sectors
        mfat_start = dir_start + dir_sectors
        ms_start = mfat_start + mfat_sectors
        large_start = ms_start + ms_sectors

        self._assign_large_sectors(large, large_blobs, large_start)

        fat = self._build_fat(fat_sectors, dir_start, dir_sectors,
                              mfat_start, mfat_sectors, ms_start, ms_sectors,
                              large, large_blobs)
        directory = self._build_directory(ms_start, ms_sectors, ms_logical)
        header = self._build_header(fat_sectors, dir_start, mfat_start, mfat_sectors)

        # Pad mini FAT
        while len(mini_fat) < mfat_sectors * _SECTOR_SIZE:
            mini_fat += struct.pack('<I', _FREESECT)

        result = bytearray(header) + fat + directory + mini_fat + mini_stream
        for path, _ in large:
            result += large_blobs[path]

        self._validate(bytes(result))
        return bytes(result)

    def _build_mini_stream(self, small):
        ms = bytearray()
        for path, _ in small:
            data = self._streams[path]
            self._info[path] = _StreamInfo(len(ms) // _MINI_SECTOR_SIZE, len(data), True)
            ms += data
            ms += b'\x00' * ((-len(ms)) % _MINI_SECTOR_SIZE)
        logical = len(ms)
        ms += b'\x00' * ((-len(ms)) % _SECTOR_SIZE)
        return bytes(ms), logical

    def _build_mini_fat(self, small):
        mf = bytearray()
        for path, _ in small:
            si = self._info[path]
            n = max(1, math.ceil(si.size / _MINI_SECTOR_SIZE))
            for i in range(n - 1):
                mf += struct.pack('<I', si.start_sector + i + 1)
            mf += struct.pack('<I', _ENDOFCHAIN)
        return mf

    def _pad_large_streams(self, large):
        blobs = {}
        for path, _ in large:
            data = self._streams[path]
            blobs[path] = data + b'\x00' * ((-len(data)) % _SECTOR_SIZE)
        return blobs

    def _assign_large_sectors(self, large, blobs, start):
        cur = start
        for path, _ in large:
            n = len(blobs[path]) // _SECTOR_SIZE
            self._info[path] = _StreamInfo(cur, len(self._streams[path]), False)
            cur += n

    def _compute_fat_sectors(self, dir_s, mfat_s, ms_s, large_s):
        fat_s = 1
        while True:
            total = fat_s + dir_s + mfat_s + ms_s + large_s
            if math.ceil(total / _FAT_PER_SECTOR) <= fat_s:
                return fat_s
            fat_s += 1

    def _build_fat(self, fat_sectors, dir_start, dir_sectors,
                   mfat_start, mfat_sectors, ms_start, ms_sectors,
                   large, large_blobs):
        fat = bytearray()
        for _ in range(fat_sectors):
            fat += struct.pack('<I', _FATSECT)
        for i in range(dir_sectors - 1):
            fat += struct.pack('<I', dir_start + i + 1)
        fat += struct.pack('<I', _ENDOFCHAIN)
        for i in range(mfat_sectors - 1):
            fat += struct.pack('<I', mfat_start + i + 1)
        fat += struct.pack('<I', _ENDOFCHAIN)
        if ms_sectors > 0:
            for i in range(ms_sectors - 1):
                fat += struct.pack('<I', ms_start + i + 1)
            fat += struct.pack('<I', _ENDOFCHAIN)
        for path, _ in large:
            si = self._info[path]
            n = len(large_blobs[path]) // _SECTOR_SIZE
            for i in range(n - 1):
                fat += struct.pack('<I', si.start_sector + i + 1)
            fat += struct.pack('<I', _ENDOFCHAIN)
        while len(fat) < fat_sectors * _SECTOR_SIZE:
            fat += struct.pack('<I', _FREESECT)
        return bytes(fat)

    def _build_directory(self, ms_start, ms_sectors, ms_logical):
        si = lambda p: self._info[p]
        de = _dir_entry

        entries = bytearray()
        entries += de('Root Entry', 5, color=1, child=7,
                      start=ms_start if ms_sectors > 0 else _ENDOFCHAIN, size=ms_logical)
        entries += de('VBA', 1, color=0, child=2)
        entries += de('ThisDocument', 2, color=1, left=3, right=4,
                      start=si('VBA/ThisDocument').start_sector, size=si('VBA/ThisDocument').size)
        entries += de('NewMacros', 2, color=1, left=5,
                      start=si('VBA/NewMacros').start_sector, size=si('VBA/NewMacros').size)
        entries += de('_VBA_PROJECT', 2, color=1,
                      start=si('VBA/_VBA_PROJECT').start_sector, size=si('VBA/_VBA_PROJECT').size)
        entries += de('dir', 2, color=0,
                      start=si('VBA/dir').start_sector, size=si('VBA/dir').size)
        entries += de('PROJECTwm', 2, color=0,
                      start=si('PROJECTwm').start_sector, size=si('PROJECTwm').size)
        entries += de('PROJECT', 2, color=1, left=1, right=6,
                      start=si('PROJECT').start_sector, size=si('PROJECT').size)
        while len(entries) < 2 * _SECTOR_SIZE:
            entries += _empty_entry()
        return bytes(entries)

    def _build_header(self, fat_sectors, dir_start, mfat_start, mfat_sectors):
        hdr = bytearray(512)
        hdr[0:8] = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
        struct.pack_into('<H', hdr, 24, 0x003E)
        struct.pack_into('<H', hdr, 26, 0x0003)
        struct.pack_into('<H', hdr, 28, 0xFFFE)
        struct.pack_into('<H', hdr, 30, 9)
        struct.pack_into('<H', hdr, 32, 6)
        struct.pack_into('<I', hdr, 44, fat_sectors)
        struct.pack_into('<I', hdr, 48, dir_start)
        struct.pack_into('<I', hdr, 56, _MINI_CUTOFF)
        struct.pack_into('<I', hdr, 60, mfat_start)
        struct.pack_into('<I', hdr, 64, mfat_sectors)
        struct.pack_into('<I', hdr, 68, _ENDOFCHAIN)
        struct.pack_into('<I', hdr, 72, 0)
        for i in range(min(fat_sectors, 109)):
            struct.pack_into('<I', hdr, 76 + i * 4, i)  # FAT starts at sector 0
        for i in range(fat_sectors, 109):
            struct.pack_into('<I', hdr, 76 + i * 4, _FREESECT)
        return bytes(hdr)

    @staticmethod
    def _validate(data: bytes):
        ole = olefile.OleFileIO(io.BytesIO(data))
        for entry in ole.listdir():
            ole.openstream(entry).read()
        ole.close()


def _dir_entry(name, etype, color=1, left=_NOSTREAM, right=_NOSTREAM,
               child=_NOSTREAM, start=_ENDOFCHAIN, size=0):
    e = bytearray(128)
    u16 = name.encode('utf-16-le')
    e[0:len(u16)] = u16
    struct.pack_into('<H', e, 64, len(u16) + 2)
    e[66] = etype
    e[67] = color
    struct.pack_into('<I', e, 68, left)
    struct.pack_into('<I', e, 72, right)
    struct.pack_into('<I', e, 76, child)
    struct.pack_into('<I', e, 116, start)
    struct.pack_into('<I', e, 120, size)
    return bytes(e)


def _empty_entry():
    e = bytearray(128)
    struct.pack_into('<I', e, 68, _NOSTREAM)
    struct.pack_into('<I', e, 72, _NOSTREAM)
    struct.pack_into('<I', e, 76, _NOSTREAM)
    struct.pack_into('<I', e, 116, _ENDOFCHAIN)
    return bytes(e)


# ---------------------------------------------------------------------------
# OOXML patching
# ---------------------------------------------------------------------------

_CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
_WNE_NS = 'http://schemas.microsoft.com/office/word/2006/wordml'


def _patch_content_types(data: bytes) -> bytes:
    tree = etree.fromstring(data)
    for ov in tree.findall(f'{{{_CT_NS}}}Override'):
        if 'wordprocessingml.document.main' in ov.get('ContentType', ''):
            ov.set('ContentType', 'application/vnd.ms-word.document.macroEnabled.main+xml')
    if not any(d.get('Extension') == 'bin' for d in tree.findall(f'{{{_CT_NS}}}Default')):
        d = etree.SubElement(tree, f'{{{_CT_NS}}}Default')
        d.set('Extension', 'bin')
        d.set('ContentType', 'application/vnd.ms-office.vbaProject')
    if not any('vbaData' in ov.get('PartName', '') for ov in tree.findall(f'{{{_CT_NS}}}Override')):
        ov = etree.SubElement(tree, f'{{{_CT_NS}}}Override')
        ov.set('PartName', '/word/vbaData.xml')
        ov.set('ContentType', 'application/vnd.ms-word.vbaData+xml')
    return etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)


def _patch_rels(data: bytes) -> bytes:
    tree = etree.fromstring(data)
    if any('vbaProject' in r.get('Target', '') for r in tree.findall(f'{{{_REL_NS}}}Relationship')):
        return data
    max_id = 0
    for r in tree.findall(f'{{{_REL_NS}}}Relationship'):
        try:
            max_id = max(max_id, int(r.get('Id', 'rId0').replace('rId', '')))
        except ValueError:
            pass
    rel = etree.SubElement(tree, f'{{{_REL_NS}}}Relationship')
    rel.set('Id', f'rId{max_id + 1}')
    rel.set('Type', 'http://schemas.microsoft.com/office/2006/relationships/vbaProject')
    rel.set('Target', 'vbaProject.bin')
    return etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)


def _build_vba_data_xml() -> bytes:
    root = etree.Element(etree.QName(_WNE_NS, 'vbaSuppData'), nsmap={'wne': _WNE_NS})
    mcds = etree.SubElement(root, etree.QName(_WNE_NS, 'mcds'))
    for macro_name, display_name in (
        ('PROJECT.NEWMACROS.AUTOOPEN', 'Project.NewMacros.AutoOpen'),
        ('PROJECT.NEWMACROS.DOCUMENT_OPEN', 'Project.NewMacros.Document_Open'),
    ):
        etree.SubElement(mcds, etree.QName(_WNE_NS, 'mcd'), attrib={
            etree.QName(_WNE_NS, 'macroName'): macro_name,
            etree.QName(_WNE_NS, 'name'): display_name,
            etree.QName(_WNE_NS, 'bEncrypt'): '00',
            etree.QName(_WNE_NS, 'cmg'): '56',
        })
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


def _build_vba_project_rels() -> bytes:
    root = etree.Element(f'{{{_REL_NS}}}Relationships', nsmap={None: _REL_NS})
    rel = etree.SubElement(root, f'{{{_REL_NS}}}Relationship')
    rel.set('Id', 'rId1')
    rel.set('Type', 'http://schemas.microsoft.com/office/2006/relationships/wordVbaData')
    rel.set('Target', 'vbaData.xml')
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_word_doc(macro_code: str, output: str | Path, content: str = "") -> Path:
    """Create a .docm with embedded VBA macros."""
    output = Path(output)
    if output.suffix != '.docm':
        output = output.with_suffix('.docm')

    # Build VBA project
    vba = VBAProject(macro_code)
    vba_bin = OLE2Builder(vba.build_streams()).build()

    # Build base OOXML with python-docx
    doc = WordDocument()
    doc.add_paragraph(content or "")
    base = io.BytesIO()
    doc.save(base)

    # Assemble .docm
    buf = io.BytesIO()
    with zipfile.ZipFile(base) as zin, zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == '[Content_Types].xml':
                data = _patch_content_types(data)
            elif item.filename == 'word/_rels/document.xml.rels':
                data = _patch_rels(data)
            zout.writestr(item, data)
        zout.writestr('word/vbaProject.bin', vba_bin)
        zout.writestr('word/vbaData.xml', _build_vba_data_xml())
        zout.writestr('word/_rels/vbaProject.bin.rels', _build_vba_project_rels())

    output.write_bytes(buf.getvalue())
    return output