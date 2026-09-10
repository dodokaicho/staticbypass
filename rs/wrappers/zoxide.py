from string import Template

class zoxide:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['use crate::cmd::{Cmd, Run};',
                'use crate::error::SilentExit;',
                'use clap::Parser;',
                'use std::env;',
                'use std::io::{{self, Write}};',
                'use std::process::ExitCode;']

    def compilerOptions(self) -> list[str]:
        return ['anyhow = "1.0.32"',
                'askama = { version = "0.16.0", default-features = false, features = ["derive","std",] }',
                'bincode = "1.3.1"',
                'clap = { version = "4.3.0", features = ["derive"] }',
                'color-print = "0.3.4"',
                'dirs = "6.0.0"',
                'dunce = "1.0.1"',
                'fastrand = "2.0.0"',
                'glob = "0.3.0"',
                'ouroboros = "0.18.3"',
                'serde = { version = "1.0.116", features = ["derive"] }',
                'time = { version = "0.3.47", default-features = false, features = ["parsing", "macros", "std"] }',
                'which = "8.0.2"'
        ]

    def template(self) -> str:
        return """
{imports}

{codeblocks}

#[allow(clippy::single_component_path_imports)]
mod cmd {{
    mod add {{
        use crate::cmd::{{Add, Run}};
        use crate::db::Database;
        use crate::{{config, util}};
        use anyhow::{{Result, bail}};
        use std::path::Path;
        impl Run for Add {{
            fn run(&self) -> Result<()> {{
                const EXCLUDE_CHARS: &[char] = &['\\n', '\\r'];
                let exclude_dirs = config::exclude_dirs()?;
                let max_age = config::maxage()?;
                let now = util::current_time()?;
                let mut db = Database::open()?;
                for path in &self.paths {{
                    let path = if config::resolve_symlinks() {{
                        util::canonicalize
                    }} else {{
                        util::resolve_path
                    }}(path)?;
                    let path = util::path_to_str(&path)?;
                    if path.contains(EXCLUDE_CHARS)
                        || exclude_dirs.iter().any(|glob| glob.matches(path))
                    {{
                        continue;
                    }}
                    if !Path::new(path).is_dir() {{
                        bail!("not a directory: {{path}}");
                    }}
                    let by = self.score.unwrap_or(1.0);
                    db.add_update(path, by, now);
                }}
                if db.dirty() {{
                    db.age(max_age);
                }}
                db.save()
            }}
        }}
    }}
    mod cmd {{
        use clap::builder::{{IntoResettable, Resettable, StyledStr}};
        use clap::{{Parser, Subcommand, ValueEnum, ValueHint}};
        use std::path::PathBuf;
        struct HelpTemplate;
        impl IntoResettable<StyledStr> for HelpTemplate {{
            fn into_resettable(self) -> Resettable<StyledStr> {{
                color_print :: cstr ! ("\\
{{before-help}}<bold><underline>{{name}} {{version}}</underline></bold>
{{author}}
https://github.com/ajeetdsouza/zoxide

{{about}}

{{usage-heading}}
{{tab}}{{usage}}

{{all-args}}{{after-help}}

<bold><underline>Environment variables:</underline></bold>
{{tab}}<bold>_ZO_DATA_DIR</bold>        {{tab}}Path for zoxide data files
{{tab}}<bold>_ZO_ECHO</bold>            {{tab}}Print the matched directory before navigating to it when set to 1
{{tab}}<bold>_ZO_EXCLUDE_DIRS</bold>    {{tab}}List of directory globs to be excluded
{{tab}}<bold>_ZO_FZF_OPTS</bold>        {{tab}}Custom flags to pass to fzf
{{tab}}<bold>_ZO_MAXAGE</bold>          {{tab}}Maximum total age after which entries start getting deleted
{{tab}}<bold>_ZO_RESOLVE_SYMLINKS</bold>{{tab}}Resolve symlinks when storing paths") . into_resettable ()
            }}
        }}
        #[derive(Debug, Parser)]
        # [clap (about , author , help_template = HelpTemplate , disable_help_subcommand = true , propagate_version = true , version ,)]
        pub enum Cmd {{
            Add(Add),
            Edit(Edit),
            Import(Import),
            Init(Init),
            Query(Query),
            Remove(Remove),
        }}
        #[doc = " Add a new directory or increment its rank"]
        #[derive(Debug, Parser)]
        # [clap (author , help_template = HelpTemplate ,)]
        pub struct Add {{
            # [clap (num_args = 1 .., required = true , value_hint = ValueHint :: DirPath)]
            pub paths: Vec<PathBuf>,
            #[doc = " The rank to increment the entry if it exists or initialize it with if it"]
            #[doc = " doesn't"]
            #[clap(short, long)]
            pub score: Option<f64>,
        }}
        #[doc = " Edit the database"]
        #[derive(Debug, Parser)]
        # [clap (author , help_template = HelpTemplate ,)]
        pub struct Edit {{
            #[clap(subcommand)]
            pub cmd: Option<EditCommand>,
        }}
        #[derive(Clone, Debug, Subcommand)]
        pub enum EditCommand {{
            #[clap(hide = true)]
            Decrement {{ path: String }},
            #[clap(hide = true)]
            Delete {{ path: String }},
            #[clap(hide = true)]
            Increment {{ path: String }},
            #[clap(hide = true)]
            Reload,
        }}
        #[doc = " Import entries from another application"]
        #[derive(Debug, Parser)]
        # [clap (author , help_template = HelpTemplate ,)]
        pub struct Import {{
            #[clap(subcommand)]
            pub from: ImportFrom,
            #[doc = " Merge into existing database"]
            #[clap(long, global = true)]
            pub merge: bool,
        }}
        #[derive(Subcommand, Clone, Debug)]
        pub enum ImportFrom {{
            #[doc = " Import from atuin"]
            Atuin,
            #[doc = " Import from autojump"]
            Autojump,
            #[doc = " Import from fasd"]
            Fasd,
            #[doc = " Import from z"]
            Z,
            #[doc = " Import from z.lua"]
            #[clap(name = "z.lua")]
            ZLua,
            #[doc = " Import from zsh-z"]
            #[clap(name = "zsh-z")]
            ZshZ,
        }}
        #[doc = " Generate shell configuration"]
        #[derive(Debug, Parser)]
        # [clap (author , help_template = HelpTemplate ,)]
        pub struct Init {{
            #[clap(value_enum)]
            pub shell: InitShell,
            #[doc = " Prevents zoxide from defining the `z` and `zi` commands"]
            #[clap(long, alias = "no-aliases")]
            pub no_cmd: bool,
            #[doc = " Changes the prefix of the `z` and `zi` commands"]
            #[clap(long, default_value = "z")]
            pub cmd: String,
            #[doc = " Changes how often zoxide increments a directory's score"]
            #[clap(value_enum, long, default_value = "pwd")]
            pub hook: InitHook,
        }}
        #[derive(ValueEnum, Clone, Copy, Debug, Eq, PartialEq)]
        pub enum InitHook {{
            None,
            Prompt,
            Pwd,
        }}
        #[derive(ValueEnum, Clone, Debug)]
        pub enum InitShell {{
            Bash,
            Elvish,
            Fish,
            Nushell,
            #[clap(alias = "ksh")]
            Posix,
            Powershell,
            Tcsh,
            Xonsh,
            Zsh,
        }}
        #[doc = " Search for a directory in the database"]
        #[derive(Debug, Parser)]
        # [clap (author , help_template = HelpTemplate ,)]
        pub struct Query {{
            pub keywords: Vec<String>,
            #[doc = " Show unavailable directories"]
            #[clap(long, short)]
            pub all: bool,
            #[doc = " Use interactive selection"]
            #[clap(long, short, conflicts_with = "list")]
            pub interactive: bool,
            #[doc = " List all matching directories"]
            #[clap(long, short, conflicts_with = "interactive")]
            pub list: bool,
            #[doc = " Print score with results"]
            #[clap(long, short)]
            pub score: bool,
            #[doc = " Exclude the current directory"]
            # [clap (long , value_hint = ValueHint :: DirPath , value_name = "path")]
            pub exclude: Option<String>,
            #[doc = " Only search within this directory"]
            # [clap (long , value_hint = ValueHint :: DirPath , value_name = "path")]
            pub base_dir: Option<String>,
        }}
        #[doc = " Remove a directory from the database"]
        #[derive(Debug, Parser)]
        # [clap (author , help_template = HelpTemplate ,)]
        pub struct Remove {{
            # [clap (value_hint = ValueHint :: DirPath)]
            pub paths: Vec<String>,
        }}
    }}
    mod edit {{
        use crate::cmd::{{Edit, EditCommand, Run}};
        use crate::db::Database;
        use crate::error::BrokenPipeHandler;
        use crate::util::{{self, Fzf, FzfChild}};
        use anyhow::Result;
        use std::io::{{self, Write}};
        impl Run for Edit {{
            fn run(&self) -> Result<()> {{
                let now = util::current_time()?;
                let db = &mut Database::open()?;
                match &self.cmd {{
                    Some(cmd) => {{
                        match cmd {{
                            EditCommand::Decrement {{ path }} => db.add(path, -1.0, now),
                            EditCommand::Delete {{ path }} => {{
                                db.remove(path);
                            }}
                            EditCommand::Increment {{ path }} => db.add(path, 1.0, now),
                            EditCommand::Reload => {{}}
                        }}
                        db.save()?;
                        let stdout = &mut io::stdout().lock();
                        for dir in db.dirs().iter().rev() {{
                            write!(
                                stdout,
                                "{{}}\\0",
                                dir.display().with_score(now).with_separator('\\t')
                            )
                            .pipe_exit("fzf")?;
                        }}
                        Ok(())
                    }}
                    None => {{
                        db.sort_by_score(now);
                        db.save()?;
                        Self::get_fzf()?.wait()?;
                        Ok(())
                    }}
                }}
            }}
        }}
        impl Edit {{
            fn get_fzf() -> Result<FzfChild> {{
                Fzf::new()?
                    .args([
                        "--exact",
                        "--no-sort",
                        "--bind=\\
btab:up,\\
ctrl-r:reload(zoxide edit reload),\\
ctrl-d:reload(zoxide edit delete {{2..}}),\\
ctrl-w:reload(zoxide edit increment {{2..}}),\\
ctrl-s:reload(zoxide edit decrement {{2..}}),\\
ctrl-z:ignore,\\
double-click:ignore,\\
enter:abort,\\
start:reload(zoxide edit reload),\\
tab:down",
                        "--cycle",
                        "--keep-right",
                        "--border=sharp",
                        "--border-label=  zoxide-edit  ",
                        "--header=\\
ctrl-r:reload   \\tctrl-d:delete
ctrl-w:increment\\tctrl-s:decrement

 SCORE\\tPATH",
                        "--info=inline",
                        "--layout=reverse",
                        "--padding=1,0,0,0",
                        "--color=label:bold",
                        "--tabstop=1",
                    ])
                    .enable_preview()
                    .spawn()
            }}
        }}
    }}
    mod import {{
        use crate::cmd::{{Import, ImportFrom, Run}};
        use crate::db::Database;
        use crate::import;
        use anyhow::{{Result, bail}};
        impl Run for Import {{
            fn run(&self) -> Result<()> {{
                let mut db = Database::open()?;
                if !self.merge && !db.dirs().is_empty() {{
                    bail!("current database is not empty, specify --merge to continue anyway");
                }}
                match self.from {{
                    ImportFrom::Atuin => import::run(&import::Atuin {{}}, &mut db)?,
                    ImportFrom::Autojump => import::run(&import::Autojump {{}}, &mut db)?,
                    ImportFrom::Fasd => import::run(&import::Fasd {{}}, &mut db)?,
                    ImportFrom::Z => import::run(&import::Z {{}}, &mut db)?,
                    ImportFrom::ZLua => import::run(&import::ZLua {{}}, &mut db)?,
                    ImportFrom::ZshZ => import::run(&import::ZshZ {{}}, &mut db)?,
                }}
                db.save()
            }}
        }}
    }}
    mod init {{
        use crate::cmd::{{Init, InitShell, Run}};
        use crate::config;
        use crate::error::BrokenPipeHandler;
        use anyhow::{{Context, Result}};
        use askama::Template;
        use std::io::{{self, Write}};
        impl Run for Init {{
            fn run(&self) -> Result<()> {{
                let cmd = if self.no_cmd {{ None }} else {{ Some(self.cmd.as_str()) }};
                let echo = config::echo();
                let resolve_symlinks = config::resolve_symlinks();
                writeln!(io::stdout(), "> ").pipe_exit("stdout")
            }}
        }}
    }}
    mod query {{
        use crate::cmd::{{Query, Run}};
        use crate::config;
        use crate::db::{{Database, Epoch, Stream, StreamOptions}};
        use crate::error::BrokenPipeHandler;
        use crate::util::{{self, Fzf, FzfChild}};
        use anyhow::{{Context, Result}};
        use std::io::{{self, Write}};
        impl Run for Query {{
            fn run(&self) -> Result<()> {{
                let mut db = crate::db::Database::open()?;
                self.query(&mut db).and(db.save())
            }}
        }}
        impl Query {{
            fn query(&self, db: &mut Database) -> Result<()> {{
                let now = util::current_time()?;
                let mut stream = self.get_stream(db, now)?;
                if self.interactive {{
                    self.query_interactive(&mut stream, now)
                }} else if self.list {{
                    self.query_list(&mut stream, now)
                }} else {{
                    self.query_first(&mut stream, now)
                }}
            }}
            fn query_interactive(&self, stream: &mut Stream, now: Epoch) -> Result<()> {{
                let mut fzf = Self::get_fzf()?;
                let selection = loop {{
                    match stream.next() {{
                        Some(dir) if Some(dir.path.as_ref()) == self.exclude.as_deref() => continue,
                        Some(dir) => {{
                            if let Some(selection) = fzf.write(dir, now)? {{
                                break selection;
                            }}
                        }}
                        None => break fzf.wait()?,
                    }}
                }};
                if self.score {{
                    print!("{{selection}}");
                }} else {{
                    let path = selection.get(7..).context("could not read selection from fzf")?;
                    print!("{{path}}");
                }}
                Ok(())
            }}
            fn query_list(&self, stream: &mut Stream, now: Epoch) -> Result<()> {{
                let handle = &mut io::stdout().lock();
                while let Some(dir) = stream.next() {{
                    if Some(dir.path.as_ref()) == self.exclude.as_deref() {{
                        continue;
                    }}
                    let dir =
                        if self.score {{ dir.display().with_score(now) }} else {{ dir.display() }};
                    writeln!(handle, "{{dir}}").pipe_exit("stdout")?;
                }}
                Ok(())
            }}
            fn query_first(&self, stream: &mut Stream, now: Epoch) -> Result<()> {{
                let handle = &mut io::stdout();
                let mut dir = stream.next().context("no match found")?;
                while Some(dir.path.as_ref()) == self.exclude.as_deref() {{
                    dir = stream.next().context("you are already in the only match")?;
                }}
                let dir = if self.score {{ dir.display().with_score(now) }} else {{ dir.display() }};
                writeln!(handle, "{{dir}}").pipe_exit("stdout")
            }}
            fn get_stream<'a>(&self, db: &'a mut Database, now: Epoch) -> Result<Stream<'a>> {{
                let mut options = StreamOptions::new(now)
                    .with_keywords(self.keywords.iter().map(|s| s.as_str()))
                    .with_exclude(config::exclude_dirs()?)
                    .with_base_dir(self.base_dir.clone());
                if !self.all {{
                    let resolve_symlinks = config::resolve_symlinks();
                    options = options.with_exists(true).with_resolve_symlinks(resolve_symlinks);
                }}
                let stream = Stream::new(db, options);
                Ok(stream)
            }}
            fn get_fzf() -> Result<FzfChild> {{
                let mut fzf = Fzf::new()?;
                if let Some(fzf_opts) = config::fzf_opts() {{
                    fzf.env("FZF_DEFAULT_OPTS", fzf_opts)
                }} else {{
                    fzf.args([
                        "--exact",
                        "--no-sort",
                        "--bind=ctrl-z:ignore,btab:up,tab:down",
                        "--cycle",
                        "--keep-right",
                        "--border=sharp",
                        "--height=45%",
                        "--info=inline",
                        "--layout=reverse",
                        "--tabstop=1",
                        "--exit-0",
                    ])
                    .enable_preview()
                }}
                .spawn()
            }}
        }}
    }}
    mod remove {{
        use crate::cmd::{{Remove, Run}};
        use crate::db::Database;
        use crate::util;
        use anyhow::{{Result, bail}};
        impl Run for Remove {{
            fn run(&self) -> Result<()> {{
                let mut db = Database::open()?;
                for path in &self.paths {{
                    if !db.remove(path) {{
                        let path_abs = util::resolve_path(path)?;
                        let path_abs = util::path_to_str(&path_abs)?;
                        if path_abs == path || !db.remove(path_abs) {{
                            bail!("path not found in database: {{path}}")
                        }}
                    }}
                }}
                db.save()
            }}
        }}
    }}
    pub use crate::cmd::cmd::*;
    use anyhow::Result;
    pub trait Run {{
        fn run(&self) -> Result<()>;
    }}
    impl Run for Cmd {{
        fn run(&self) -> Result<()> {{
            match self {{
                Cmd::Add(cmd) => cmd.run(),
                Cmd::Edit(cmd) => cmd.run(),
                Cmd::Import(cmd) => cmd.run(),
                Cmd::Init(cmd) => cmd.run(),
                Cmd::Query(cmd) => cmd.run(),
                Cmd::Remove(cmd) => cmd.run(),
            }}
        }}
    }}
}}
mod config {{
    use crate::db::Rank;
    use anyhow::{{Context, Result, ensure}};
    use glob::Pattern;
    use std::env;
    use std::ffi::OsString;
    use std::path::PathBuf;
    pub fn data_dir() -> Result<PathBuf> {{
        let dir = match env::var_os("_ZO_DATA_DIR") {{
            Some(path) => PathBuf::from(path),
            None => dirs::data_local_dir()
                .context("could not find data directory, please set _ZO_DATA_DIR manually")?
                .join("zoxide"),
        }};
        ensure!(dir.is_absolute(), "_ZO_DATA_DIR must be an absolute path");
        Ok(dir)
    }}
    pub fn echo() -> bool {{
        env::var_os("_ZO_ECHO").is_some_and(|var| var == "1")
    }}
    pub fn exclude_dirs() -> Result<Vec<Pattern>> {{
        match env::var_os("_ZO_EXCLUDE_DIRS") {{
            Some(paths) => env::split_paths(&paths)
                .map(|path| {{
                    let pattern = path.to_str().context("invalid unicode in _ZO_EXCLUDE_DIRS")?;
                    Pattern::new(pattern)
                        .with_context(|| format!("invalid glob in _ZO_EXCLUDE_DIRS: {{pattern}}"))
                }})
                .collect(),
            None => {{
                let pattern = (|| {{
                    let home = dirs::home_dir()?;
                    let home = Pattern::escape(home.to_str()?);
                    Pattern::new(&home).ok()
                }})();
                Ok(pattern.into_iter().collect())
            }}
        }}
    }}
    pub fn fzf_opts() -> Option<OsString> {{
        env::var_os("_ZO_FZF_OPTS")
    }}
    pub fn maxage() -> Result<Rank> {{
        env::var_os("_ZO_MAXAGE").map_or(Ok(10_000.0), |maxage| {{
            let maxage = maxage.to_str().context("invalid unicode in _ZO_MAXAGE")?;
            let maxage = maxage
                .parse::<u32>()
                .with_context(|| format!("unable to parse _ZO_MAXAGE as integer: {{maxage}}"))?;
            Ok(maxage as Rank)
        }})
    }}
    pub fn resolve_symlinks() -> bool {{
        env::var_os("_ZO_RESOLVE_SYMLINKS").is_some_and(|var| var == "1")
    }}
}}
mod db {{
    mod dir {{
        use crate::util::{{DAY, HOUR, WEEK}};
        use serde::{{Deserialize, Serialize}};
        use std::borrow::Cow;
        use std::fmt::{{self, Display, Formatter}};
        #[derive(Clone, Debug, Deserialize, Serialize)]
        pub struct Dir<'a> {{
            #[serde(borrow)]
            pub path: Cow<'a, str>,
            pub rank: Rank,
            pub last_accessed: Epoch,
        }}
        impl Dir<'_> {{
            pub fn display(&self) -> DirDisplay<'_> {{
                DirDisplay::new(self)
            }}
            pub fn score(&self, now: Epoch) -> Rank {{
                let duration = now.saturating_sub(self.last_accessed);
                if duration < HOUR {{
                    self.rank * 4.0
                }} else if duration < DAY {{
                    self.rank * 2.0
                }} else if duration < WEEK {{
                    self.rank * 0.5
                }} else {{
                    self.rank * 0.25
                }}
            }}
        }}
        pub struct DirDisplay<'a> {{
            dir: &'a Dir<'a>,
            now: Option<Epoch>,
            separator: char,
        }}
        impl<'a> DirDisplay<'a> {{
            fn new(dir: &'a Dir) -> Self {{
                Self {{ dir, separator: ' ', now: None }}
            }}
            pub fn with_score(mut self, now: Epoch) -> Self {{
                self.now = Some(now);
                self
            }}
            pub fn with_separator(mut self, separator: char) -> Self {{
                self.separator = separator;
                self
            }}
        }}
        impl Display for DirDisplay<'_> {{
            fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {{
                if let Some(now) = self.now {{
                    let score = self.dir.score(now).clamp(0.0, 9999.0);
                    write!(f, "{{score:>6.1}}{{}}", self.separator)?;
                }}
                write!(f, "{{}}", self.dir.path)
            }}
        }}
        pub type Rank = f64;
        pub type Epoch = u64;
    }}
    mod stream {{
        use crate::db::{{Database, Dir, Epoch}};
        use crate::util::{{self, MONTH}};
        use glob::Pattern;
        use std::iter::Rev;
        use std::ops::Range;
        use std::path::Path;
        use std::{{fs, path}};
        pub struct Stream<'a> {{
            db: &'a mut Database,
            idxs: Rev<Range<usize>>,
            options: StreamOptions,
        }}
        impl<'a> Stream<'a> {{
            pub fn new(db: &'a mut Database, options: StreamOptions) -> Self {{
                db.sort_by_score(options.now);
                let idxs = (0..db.dirs().len()).rev();
                Stream {{ db, idxs, options }}
            }}
            pub fn next(&mut self) -> Option<&Dir<'_>> {{
                while let Some(idx) = self.idxs.next() {{
                    let dir = &self.db.dirs()[idx];
                    if !self.filter_by_keywords(&dir.path) {{
                        continue;
                    }}
                    if !self.filter_by_base_dir(&dir.path) {{
                        continue;
                    }}
                    if !self.filter_by_exclude(&dir.path) {{
                        self.db.swap_remove(idx);
                        continue;
                    }}
                    if !self.filter_by_exists(&dir.path) {{
                        if dir.last_accessed < self.options.ttl {{
                            self.db.swap_remove(idx);
                        }}
                        continue;
                    }}
                    let dir = &self.db.dirs()[idx];
                    return Some(dir);
                }}
                None
            }}
            fn filter_by_base_dir(&self, path: &str) -> bool {{
                match &self.options.base_dir {{
                    Some(base_dir) => Path::new(path).starts_with(base_dir),
                    None => true,
                }}
            }}
            fn filter_by_exclude(&self, path: &str) -> bool {{
                !self.options.exclude.iter().any(|pattern| pattern.matches(path))
            }}
            fn filter_by_exists(&self, path: &str) -> bool {{
                if !self.options.exists {{
                    return true;
                }}
                let resolver =
                    if self.options.resolve_symlinks {{ fs::symlink_metadata }} else {{ fs::metadata }};
                resolver(path).map(|metadata| metadata.is_dir()).unwrap_or_default()
            }}
            fn filter_by_keywords(&self, path: &str) -> bool {{
                let (keywords_last, keywords) = match self.options.keywords.split_last() {{
                    Some(split) => split,
                    None => return true,
                }};
                let path = util::to_lowercase(path);
                let mut path = path.as_str();
                match path.rfind(keywords_last) {{
                    Some(idx) => {{
                        if path[idx + keywords_last.len()..].contains(path::is_separator) {{
                            return false;
                        }}
                        path = &path[..idx];
                    }}
                    None => return false,
                }}
                for keyword in keywords.iter().rev() {{
                    match path.rfind(keyword) {{
                        Some(idx) => path = &path[..idx],
                        None => return false,
                    }}
                }}
                true
            }}
        }}
        pub struct StreamOptions {{
            #[doc = " The current time."]
            now: Epoch,
            #[doc = " Only directories matching these keywords will be returned."]
            keywords: Vec<String>,
            #[doc = " Directories that match any of these globs will be lazily removed."]
            exclude: Vec<Pattern>,
            #[doc = " Directories will only be returned if they exist on the filesystem."]
            exists: bool,
            #[doc = " Whether to resolve symlinks when checking if a directory exists."]
            resolve_symlinks: bool,
            #[doc = " Directories that do not exist and haven't been accessed since TTL will"]
            #[doc = " be lazily removed."]
            ttl: Epoch,
            #[doc = " Only return directories within this parent directory"]
            #[doc = " Does not check if the path exists"]
            base_dir: Option<String>,
        }}
        impl StreamOptions {{
            pub fn new(now: Epoch) -> Self {{
                StreamOptions {{
                    now,
                    keywords: Vec::new(),
                    exclude: Vec::new(),
                    exists: false,
                    resolve_symlinks: false,
                    ttl: now.saturating_sub(3 * MONTH),
                    base_dir: None,
                }}
            }}
            pub fn with_keywords<I>(mut self, keywords: I) -> Self
            where
                I: IntoIterator,
                I::Item: AsRef<str>,
            {{
                self.keywords = keywords.into_iter().map(util::to_lowercase).collect();
                self
            }}
            pub fn with_exclude(mut self, exclude: Vec<Pattern>) -> Self {{
                self.exclude = exclude;
                self
            }}
            pub fn with_exists(mut self, exists: bool) -> Self {{
                self.exists = exists;
                self
            }}
            pub fn with_resolve_symlinks(mut self, resolve_symlinks: bool) -> Self {{
                self.resolve_symlinks = resolve_symlinks;
                self
            }}
            pub fn with_base_dir(mut self, base_dir: Option<String>) -> Self {{
                self.base_dir = base_dir;
                self
            }}
        }}
        #[cfg(test)]
        mod tests {{
            use super::*;
            use rstest::rstest;
            use std::path::PathBuf;
            #[rstest]
            # [case (& ["fOo" , "bAr"] , "/foo/bar" , true)]
            # [case (& ["ba"] , "/foo/bar" , true)]
            # [case (& ["fo"] , "/foo/bar" , false)]
            # [case (& ["foo/"] , "/foo" , false)]
            # [case (& ["foo/"] , "/foo/bar" , true)]
            # [case (& ["foo/"] , "/foo/bar/baz" , false)]
            # [case (& ["foo" , "/"] , "/foo" , false)]
            # [case (& ["foo" , "/"] , "/foo/bar" , true)]
            # [case (& ["foo" , "/"] , "/foo/bar/baz" , true)]
            # [case (& ["/" , "fo" , "/" , "ar"] , "/foo/bar" , true)]
            # [case (& ["oo/ba"] , "/foo/bar" , true)]
            # [case (& ["foo" , "o" , "bar"] , "/foo/bar" , false)]
            # [case (& ["/foo/" , "/bar"] , "/foo/bar" , false)]
            # [case (& ["/foo/" , "/bar"] , "/foo/baz/bar" , true)]
            fn query(#[case] keywords: &[&str], #[case] path: &str, #[case] is_match: bool) {{
                let db = &mut Database::new(PathBuf::new(), Vec::new(), |_| Vec::new(), false);
                let options = StreamOptions::new(0).with_keywords(keywords.iter());
                let stream = Stream::new(db, options);
                assert_eq!(is_match, stream.filter_by_keywords(path));
            }}
        }}
    }}
    pub use crate::db::dir::{{Dir, Epoch, Rank}};
    pub use crate::db::stream::{{Stream, StreamOptions}};
    use crate::{{config, util}};
    use anyhow::{{Context, Result, bail}};
    use bincode::Options;
    use ouroboros::self_referencing;
    use std::path::{{Path, PathBuf}};
    use std::{{fs, io}};
    #[self_referencing]
    pub struct Database {{
        path: PathBuf,
        bytes: Vec<u8>,
        #[borrows(bytes)]
        #[covariant]
        pub dirs: Vec<Dir<'this>>,
        dirty: bool,
    }}
    impl Database {{
        const VERSION: u32 = 3;
        pub fn open() -> Result<Self> {{
            let data_dir = config::data_dir()?;
            Self::open_dir(data_dir)
        }}
        pub fn open_dir(data_dir: impl AsRef<Path>) -> Result<Self> {{
            let data_dir = data_dir.as_ref();
            let path = data_dir.join("db.zo");
            let path = fs::canonicalize(&path).unwrap_or(path);
            match fs::read(&path) {{
                Ok(bytes) => Self::try_new(path, bytes, |bytes| Self::deserialize(bytes), false),
                Err(e) if e.kind() == io::ErrorKind::NotFound => {{
                    fs::create_dir_all(data_dir).with_context(|| {{
                        format!("unable to create data directory: {{}}", data_dir.display())
                    }})?;
                    Ok(Self::new(path, Vec::new(), |_| Vec::new(), false))
                }}
                Err(e) => Err(e)
                    .with_context(|| format!("could not read from database: {{}}", path.display())),
            }}
        }}
        pub fn save(&mut self) -> Result<()> {{
            if !self.dirty() {{
                return Ok(());
            }}
            let bytes = Self::serialize(self.dirs())?;
            util::write(self.borrow_path(), bytes).context("could not write to database")?;
            self.with_dirty_mut(|dirty| *dirty = false);
            Ok(())
        }}
        #[doc = " Increments the rank of a directory, or creates it if it does not exist."]
        pub fn add(&mut self, path: impl AsRef<str> + Into<String>, by: Rank, now: Epoch) {{
            self.with_dirs_mut(|dirs| {{
                match dirs.iter_mut().find(|dir| dir.path == path.as_ref()) {{
                    Some(dir) => dir.rank = (dir.rank + by).max(0.0),
                    None => dirs.push(Dir {{
                        path: path.into().into(),
                        rank: by.max(0.0),
                        last_accessed: now,
                    }}),
                }}
            }});
            self.with_dirty_mut(|dirty| *dirty = true);
        }}
        #[doc = " Creates a new directory. This will create a duplicate entry if this"]
        #[doc = " directory is already in the database, it is expected that the user"]
        #[doc = " either does a check before calling this, or calls `dedup()`"]
        #[doc = " afterward."]
        pub fn add_unchecked(
            &mut self,
            path: impl AsRef<str> + Into<String>,
            rank: Rank,
            now: Epoch,
        ) {{
            self.with_dirs_mut(|dirs| {{
                dirs.push(Dir {{ path: path.into().into(), rank, last_accessed: now }})
            }});
            self.with_dirty_mut(|dirty| *dirty = true);
        }}
        #[doc = " Increments the rank and updates the last_accessed of a directory, or"]
        #[doc = " creates it if it does not exist."]
        pub fn add_update(&mut self, path: impl AsRef<str> + Into<String>, by: Rank, now: Epoch) {{
            self.with_dirs_mut(|dirs| {{
                match dirs.iter_mut().find(|dir| dir.path == path.as_ref()) {{
                    Some(dir) => {{
                        dir.rank = (dir.rank + by).max(0.0);
                        dir.last_accessed = now;
                    }}
                    None => dirs.push(Dir {{
                        path: path.into().into(),
                        rank: by.max(0.0),
                        last_accessed: now,
                    }}),
                }}
            }});
            self.with_dirty_mut(|dirty| *dirty = true);
        }}
        #[doc = " Removes the directory with `path` from the store. This does not preserve"]
        #[doc = " ordering, but is O(1)."]
        pub fn remove(&mut self, path: impl AsRef<str>) -> bool {{
            match self.dirs().iter().position(|dir| dir.path == path.as_ref()) {{
                Some(idx) => {{
                    self.swap_remove(idx);
                    true
                }}
                None => false,
            }}
        }}
        pub fn swap_remove(&mut self, idx: usize) {{
            self.with_dirs_mut(|dirs| dirs.swap_remove(idx));
            self.with_dirty_mut(|dirty| *dirty = true);
        }}
        pub fn age(&mut self, max_age: Rank) {{
            let mut dirty = false;
            self.with_dirs_mut(|dirs| {{
                let total_age = dirs.iter().map(|dir| dir.rank).sum::<Rank>();
                if total_age > max_age {{
                    let factor = 0.9 * max_age / total_age;
                    for idx in (0..dirs.len()).rev() {{
                        let dir = &mut dirs[idx];
                        dir.rank *= factor;
                        if dir.rank < 1.0 {{
                            dirs.swap_remove(idx);
                        }}
                    }}
                    dirty = true;
                }}
            }});
            self.with_dirty_mut(|dirty_prev| *dirty_prev |= dirty);
        }}
        pub fn dedup(&mut self) {{
            self.sort_by_path();
            let mut dirty = false;
            self.with_dirs_mut(|dirs| {{
                for idx in (1..dirs.len()).rev() {{
                    let curr_dir = &dirs[idx];
                    let next_dir = &dirs[idx - 1];
                    if next_dir.path != curr_dir.path {{
                        continue;
                    }}
                    let rank = curr_dir.rank;
                    let last_accessed = curr_dir.last_accessed;
                    let next_dir = &mut dirs[idx - 1];
                    next_dir.last_accessed = next_dir.last_accessed.max(last_accessed);
                    next_dir.rank += rank;
                    dirs.swap_remove(idx);
                    dirty = true;
                }}
            }});
            self.with_dirty_mut(|dirty_prev| *dirty_prev |= dirty);
        }}
        pub fn sort_by_path(&mut self) {{
            self.with_dirs_mut(|dirs| {{
                dirs.sort_unstable_by(|dir1, dir2| dir1.path.cmp(&dir2.path))
            }});
            self.with_dirty_mut(|dirty| *dirty = true);
        }}
        pub fn sort_by_score(&mut self, now: Epoch) {{
            self.with_dirs_mut(|dirs| {{
                dirs.sort_unstable_by(|dir1: &Dir, dir2: &Dir| {{
                    dir1.score(now).total_cmp(&dir2.score(now))
                }})
            }});
            self.with_dirty_mut(|dirty| *dirty = true);
        }}
        pub fn dirty(&self) -> bool {{
            *self.borrow_dirty()
        }}
        pub fn dirs(&self) -> &[Dir<'_>] {{
            self.borrow_dirs()
        }}
        fn serialize(dirs: &[Dir<'_>]) -> Result<Vec<u8>> {{
            (|| -> bincode::Result<_> {{
                let buffer_size =
                    bincode::serialized_size(&Self::VERSION)? + bincode::serialized_size(&dirs)?;
                let mut buffer = Vec::with_capacity(buffer_size as usize);
                bincode::serialize_into(&mut buffer, &Self::VERSION)?;
                bincode::serialize_into(&mut buffer, &dirs)?;
                Ok(buffer)
            }})()
            .context("could not serialize database")
        }}
        fn deserialize(bytes: &[u8]) -> Result<Vec<Dir<'_>>> {{
            const MAX_SIZE: u64 = 32 << 20;
            let deserializer = &mut bincode::options().with_fixint_encoding().with_limit(MAX_SIZE);
            let version_size = deserializer.serialized_size(&Self::VERSION).unwrap() as _;
            if bytes.len() < version_size {{
                bail!("could not deserialize database: corrupted data");
            }}
            let (bytes_version, bytes_dirs) = bytes.split_at(version_size);
            let version = deserializer.deserialize(bytes_version)?;
            let dirs = match version {{
                Self::VERSION => deserializer
                    .deserialize(bytes_dirs)
                    .context("could not deserialize database")?,
                version => {{
                    bail!("unsupported version (got {{version}}, supports {{}})", Self::VERSION)
                }}
            }};
            Ok(dirs)
        }}
    }}
    #[cfg(test)]
    mod tests {{
        use super::*;
        #[test]
        fn add() {{
            let data_dir = tempfile::tempdir().unwrap();
            let path = if cfg!(windows) {{ r"C:\\foo\\bar" }} else {{ "/foo/bar" }};
            let now = 946684800;
            {{
                let mut db = Database::open_dir(data_dir.path()).unwrap();
                db.add(path, 1.0, now);
                db.add(path, 1.0, now);
                db.save().unwrap();
            }}
            {{
                let db = Database::open_dir(data_dir.path()).unwrap();
                assert_eq!(db.dirs().len(), 1);
                let dir = &db.dirs()[0];
                assert_eq!(dir.path, path);
                assert!((dir.rank - 2.0).abs() < 0.01);
                assert_eq!(dir.last_accessed, now);
            }}
        }}
        #[test]
        fn remove() {{
            let data_dir = tempfile::tempdir().unwrap();
            let path = if cfg!(windows) {{ r"C:\\foo\\bar" }} else {{ "/foo/bar" }};
            let now = 946684800;
            {{
                let mut db = Database::open_dir(data_dir.path()).unwrap();
                db.add(path, 1.0, now);
                db.save().unwrap();
            }}
            {{
                let mut db = Database::open_dir(data_dir.path()).unwrap();
                assert!(db.remove(path));
                db.save().unwrap();
            }}
            {{
                let mut db = Database::open_dir(data_dir.path()).unwrap();
                assert!(db.dirs().is_empty());
                assert!(!db.remove(path));
                db.save().unwrap();
            }}
        }}
    }}
}}
mod error {{
    use anyhow::{{Context, Result, bail}};
    use std::fmt::{{self, Display, Formatter}};
    use std::io;
    #[doc = " Custom error type for early exit."]
    #[derive(Debug)]
    pub struct SilentExit {{
        pub code: u8,
    }}
    impl Display for SilentExit {{
        fn fmt(&self, _: &mut Formatter<'_>) -> fmt::Result {{
            Ok(())
        }}
    }}
    pub trait BrokenPipeHandler {{
        fn pipe_exit(self, device: &str) -> Result<()>;
    }}
    impl BrokenPipeHandler for io::Result<()> {{
        fn pipe_exit(self, device: &str) -> Result<()> {{
            match self {{
                Err(e) if e.kind() == io::ErrorKind::BrokenPipe => bail!(SilentExit {{ code: 0 }}),
                result => result.with_context(|| format!("could not write to {{device}}")),
            }}
        }}
    }}
}}
mod import {{
    pub(crate) use crate::import::atuin::Atuin;
    pub(crate) use crate::import::autojump::Autojump;
    pub(crate) use crate::import::fasd::Fasd;
    pub(crate) use crate::import::z::Z;
    pub(crate) use crate::import::z_lua::ZLua;
    pub(crate) use crate::import::zsh_z::ZshZ;
    mod atuin {{
        use crate::db::{{Dir, Epoch}};
        use crate::import::{{ImportError, Importer}};
        use anyhow::{{Context, Result, anyhow}};
        use std::borrow::Cow;
        use std::io::{{BufRead, BufReader}};
        use std::process::{{Child, ChildStdout, Command, Stdio}};
        use std::str;
        #[derive(clap :: Args, Clone, Debug)]
        pub(crate) struct Atuin {{}}
        impl Importer for Atuin {{
            fn dirs(&self) -> Result<impl Iterator<Item = Result<Dir<'static>, ImportError>>> {{
                let mut child = Command::new("atuin")
                    .args(["history", "list", "--format={{time}}\\t{{directory}}", "--print0"])
                    .stdout(Stdio::piped())
                    .spawn()
                    .context("failed to run `atuin`; is it installed and on PATH?")?;
                let stdout = child.stdout.take().expect("stdout piped");
                let reader = BufReader::new(stdout);
                Ok(Iter::new(reader, child))
            }}
        }}
        #[doc = " Iterates atuin's NUL-separated `{{time}}\\\\t{{directory}}` records, emitting one"]
        #[doc = " `Dir` per directory transition (consecutive same-path records collapse)."]
        #[doc = " Owns the `Child` handle so the subprocess is reaped on Drop."]
        struct Iter {{
            reader: BufReader<ChildStdout>,
            buf: Vec<u8>,
            line_num: usize,
            child: Child,
            prev_cwd: Option<String>,
        }}
        impl Iter {{
            fn new(reader: BufReader<ChildStdout>, child: Child) -> Self {{
                Self {{ reader, buf: Vec::new(), line_num: 0, child, prev_cwd: None }}
            }}
            fn err(&self, source: anyhow::Error) -> ImportError {{
                ImportError {{ path: None, line_num: self.line_num, source }}
            }}
            fn parse_line(&self, line: &[u8]) -> Result<Dir<'static>, ImportError> {{
                let line = str::from_utf8(line)
                    .map_err(|e| self.err(anyhow!(e).context("invalid utf-8")))?;
                let (timestamp, path) = line
                    .split_once('\\t')
                    .ok_or_else(|| self.err(anyhow!("invalid entry: {{line}}")))?;
                let timestamp_format = time::macros::format_description!(
                    "[year]-[month]-[day] [hour]:[minute]:[second]"
                );
                let timestamp = time::PrimitiveDateTime::parse(timestamp, timestamp_format)
                    .map_err(|e| {{
                        self.err(anyhow!(e).context(format!("invalid timestamp: {{timestamp:?}}")))
                    }})?
                    .assume_utc()
                    .unix_timestamp();
                let dir = Dir {{
                    path: Cow::Owned(path.to_string()),
                    rank: 1.0,
                    last_accessed: timestamp as Epoch,
                }};
                Ok(dir)
            }}
        }}
        impl Iterator for Iter {{
            type Item = Result<Dir<'static>, ImportError>;
            fn next(&mut self) -> Option<Self::Item> {{
                loop {{
                    self.buf.clear();
                    self.line_num += 1;
                    match self.reader.read_until(b'\\0', &mut self.buf) {{
                        Ok(0) => return None,
                        Ok(_) => {{
                            if self.buf.last() == Some(&b'\\0') {{
                                self.buf.pop();
                            }}
                            if self.buf.is_empty() {{
                                continue;
                            }}
                            let result = self.parse_line(&self.buf);
                            match &result {{
                                Ok(dir) => {{
                                    let path = dir.path.as_ref();
                                    if self.prev_cwd.as_deref() == Some(path) {{
                                        continue;
                                    }}
                                    self.prev_cwd = Some(path.to_string());
                                    return Some(result);
                                }}
                                Err(_) => return Some(result),
                            }}
                        }}
                        Err(e) => {{
                            return Some(Err(
                                self.err(anyhow!(e).context("could not read from atuin"))
                            ));
                        }}
                    }}
                }}
            }}
        }}
        impl Drop for Iter {{
            fn drop(&mut self) {{
                _ = self.child.kill();
                _ = self.child.wait();
            }}
        }}
    }}
    mod autojump {{
        use crate::db::Dir;
        use crate::import::{{ImportError, Importer}};
        use anyhow::{{Context, Result, anyhow}};
        use std::borrow::Cow;
        use std::fs::File;
        use std::io::{{BufRead, BufReader}};
        use std::path::PathBuf;
        use std::{{env, str}};
        #[derive(clap :: Args, Clone, Debug)]
        pub(crate) struct Autojump {{}}
        impl Importer for Autojump {{
            fn dirs(&self) -> Result<impl Iterator<Item = Result<Dir<'static>, ImportError>>> {{
                let path = data_path()?;
                let file = File::open(&path).with_context(|| format!("could not read {{path:?}}"))?;
                let reader = BufReader::new(file);
                Ok(Iter::new(reader, path))
            }}
        }}
        struct Iter<R: BufRead> {{
            reader: R,
            buf: Vec<u8>,
            line_num: usize,
            path: PathBuf,
        }}
        impl<R: BufRead> Iter<R> {{
            fn new(reader: R, path: PathBuf) -> Self {{
                Self {{ reader, buf: Vec::new(), line_num: 0, path }}
            }}
            fn err(&self, source: anyhow::Error) -> ImportError {{
                ImportError {{ path: Some(self.path.clone()), line_num: self.line_num, source }}
            }}
            fn parse_line(&self, line: &[u8]) -> Result<Dir<'static>, ImportError> {{
                let line = str::from_utf8(line)
                    .map_err(|e| self.err(anyhow!(e).context("invalid utf-8")))?;
                let (rank, path) = line
                    .split_once('\\t')
                    .ok_or_else(|| self.err(anyhow!("invalid entry: {{line}}")))?;
                let rank = rank
                    .parse::<f64>()
                    .map_err(|e| self.err(anyhow!(e).context(format!("invalid rank: {{rank}}"))))?;
                let rank = sigmoid(rank);
                Ok(Dir {{ path: Cow::Owned(path.to_string()), rank, last_accessed: 0 }})
            }}
        }}
        impl<R: BufRead> Iterator for Iter<R> {{
            type Item = Result<Dir<'static>, ImportError>;
            fn next(&mut self) -> Option<Self::Item> {{
                loop {{
                    self.buf.clear();
                    self.line_num += 1;
                    match self.reader.read_until(b'\\n', &mut self.buf) {{
                        Ok(0) => return None,
                        Ok(_) => {{
                            if self.buf.last() == Some(&b'\\n') {{
                                self.buf.pop();
                            }}
                            if self.buf.last() == Some(&b'\\r') {{
                                self.buf.pop();
                            }}
                            if self.buf.is_empty() {{
                                continue;
                            }}
                            return Some(self.parse_line(&self.buf));
                        }}
                        Err(e) => return Some(Err(self.err(anyhow::Error::from(e)))),
                    }}
                }}
            }}
        }}
        #[doc = " Mirrors autojump's path logic:"]
        #[doc = ""]
        #[doc = " ```python"]
        #[doc = " if is_osx():"]
        #[doc = "     data_home = os.path.join(os.path.expanduser('~'), 'Library')"]
        #[doc = " elif is_windows():"]
        #[doc = "     data_home = os.getenv('APPDATA')"]
        #[doc = " else:"]
        #[doc = "     data_home = os.getenv("]
        #[doc = "         'XDG_DATA_HOME',"]
        #[doc = "         os.path.join(os.path.expanduser('~'), '.local', 'share'),"]
        #[doc = "     )"]
        #[doc = " data_path = os.path.join(data_home, 'autojump', 'autojump.txt')"]
        #[doc = " ```"]
        fn data_path() -> Result<PathBuf> {{
            let mut path = if cfg!(target_os = "macos") {{
                let mut path = dirs::home_dir().context("could not find home directory")?;
                path.push("Library");
                path
            }} else if cfg!(target_os = "windows") {{
                let appdata = env::var_os("APPDATA").context("%APPDATA% is not set")?;
                PathBuf::from(appdata)
            }} else if let Some(xdg) = env::var_os("XDG_DATA_HOME") {{
                PathBuf::from(xdg)
            }} else {{
                let mut path = dirs::home_dir().context("could not find home directory")?;
                path.push(".local");
                path.push("share");
                path
            }};
            path.push("autojump");
            path.push("autojump.txt");
            Ok(path)
        }}
        fn sigmoid(x: f64) -> f64 {{
            1.0 / (1.0 + (-x).exp())
        }}
    }}
    mod fasd {{
        use crate::db::Dir;
        use crate::import::{{ImportError, Importer, z}};
        use anyhow::{{Context, Result}};
        use std::env;
        use std::fs::File;
        use std::io::BufReader;
        use std::path::PathBuf;
        #[derive(clap :: Args, Clone, Debug)]
        pub(crate) struct Fasd {{}}
        impl Importer for Fasd {{
            fn dirs(&self) -> Result<impl Iterator<Item = Result<Dir<'static>, ImportError>>> {{
                let path = data_path()?;
                let file = File::open(&path).with_context(|| format!("could not read {{path:?}}"))?;
                let reader = BufReader::new(file);
                Ok(z::Iter::new(reader, path))
            }}
        }}
        #[doc = " Mirrors fasd's path logic:"]
        #[doc = ""]
        #[doc = " ```sh"]
        #[doc = " [ -z \\"$_FASD_DATA\\" ] && _FASD_DATA=\\"$HOME/.fasd\\""]
        #[doc = " ```"]
        fn data_path() -> Result<PathBuf> {{
            match env::var_os("_FASD_DATA") {{
                Some(path) => Ok(PathBuf::from(path)),
                None => {{
                    let mut path = dirs::home_dir().context("could not find home directory")?;
                    path.push(".fasd");
                    Ok(path)
                }}
            }}
        }}
    }}
    mod z {{
        use crate::db::Dir;
        use crate::import::{{ImportError, Importer}};
        use anyhow::{{Context, Result, anyhow}};
        use std::borrow::Cow;
        use std::fs::File;
        use std::io::{{BufRead, BufReader}};
        use std::path::PathBuf;
        use std::{{env, str}};
        #[derive(clap :: Args, Clone, Debug)]
        pub(crate) struct Z {{}}
        impl Importer for Z {{
            fn dirs(&self) -> Result<impl Iterator<Item = Result<Dir<'static>, ImportError>>> {{
                let path = data_path()?;
                let file = File::open(&path).with_context(|| format!("could not read {{path:?}}"))?;
                let reader = BufReader::new(file);
                Ok(Iter::new(reader, path))
            }}
        }}
        pub(crate) struct Iter<R: BufRead> {{
            reader: R,
            buf: Vec<u8>,
            line_num: usize,
            path: PathBuf,
        }}
        impl<R: BufRead> Iter<R> {{
            pub(crate) fn new(reader: R, path: PathBuf) -> Self {{
                Self {{ reader, buf: Vec::new(), line_num: 0, path }}
            }}
            fn err(&self, source: anyhow::Error) -> ImportError {{
                ImportError {{ path: Some(self.path.clone()), line_num: self.line_num, source }}
            }}
            fn parse_line(&self, line: &[u8]) -> Result<Dir<'static>, ImportError> {{
                let line = str::from_utf8(line)
                    .map_err(|e| self.err(anyhow!(e).context("invalid utf-8")))?;
                let err = || self.err(anyhow!("invalid entry: {{line}}"));
                let mut split = line.rsplitn(3, '|');
                let last_accessed = split.next().ok_or_else(err)?;
                let last_accessed = last_accessed.parse::<u64>().map_err(|_| err())?;
                let rank = split.next().ok_or_else(err)?;
                let rank = rank.parse::<f64>().map_err(|_| err())?;
                let path = split.next().ok_or_else(err)?;
                Ok(Dir {{ path: Cow::Owned(path.to_string()), rank, last_accessed }})
            }}
        }}
        impl<R: BufRead> Iterator for Iter<R> {{
            type Item = Result<Dir<'static>, ImportError>;
            fn next(&mut self) -> Option<Self::Item> {{
                loop {{
                    self.buf.clear();
                    self.line_num += 1;
                    match self.reader.read_until(b'\\n', &mut self.buf) {{
                        Ok(0) => return None,
                        Ok(_) => {{
                            if self.buf.last() == Some(&b'\\n') {{
                                self.buf.pop();
                            }}
                            if self.buf.last() == Some(&b'\\r') {{
                                self.buf.pop();
                            }}
                            if self.buf.is_empty() {{
                                continue;
                            }}
                            return Some(self.parse_line(&self.buf));
                        }}
                        Err(e) => return Some(Err(self.err(anyhow::Error::from(e)))),
                    }}
                }}
            }}
        }}
        #[doc = " Mirrors z's path logic:"]
        #[doc = ""]
        #[doc = " ```sh"]
        #[doc = " local datafile=\\"${{_Z_DATA:-$HOME/.z}}\\""]
        #[doc = " ```"]
        fn data_path() -> Result<PathBuf> {{
            match env::var_os("_Z_DATA") {{
                Some(path) => Ok(PathBuf::from(path)),
                None => {{
                    let mut path = dirs::home_dir().context("could not find home directory")?;
                    path.push(".z");
                    Ok(path)
                }}
            }}
        }}
    }}
    mod z_lua {{
        use crate::db::Dir;
        use crate::import::{{ImportError, Importer, z}};
        use anyhow::{{Context, Result}};
        use std::env;
        use std::ffi::OsStr;
        use std::fs::File;
        use std::io::{{self, BufReader}};
        use std::path::PathBuf;
        #[derive(clap :: Args, Clone, Debug)]
        pub(crate) struct ZLua {{}}
        impl Importer for ZLua {{
            fn dirs(&self) -> Result<impl Iterator<Item = Result<Dir<'static>, ImportError>>> {{
                let path = data_path()?;
                let err = match File::open(&path) {{
                    Ok(file) => return Ok(z::Iter::new(BufReader::new(file), path)),
                    Err(e) if e.kind() == io::ErrorKind::NotFound => e,
                    Err(e) => return Err(e).with_context(|| format!("could not read {{path:?}}")),
                }};
                let fish_path = data_path_fish()?;
                let file = match File::open(&fish_path) {{
                    Ok(file) => file,
                    Err(e) if e.kind() == io::ErrorKind::NotFound => {{
                        return Err(err).with_context(|| format!("could not read {{path:?}}"));
                    }}
                    Err(e) => {{
                        return Err(e).with_context(|| format!("could not read {{fish_path:?}}"));
                    }}
                }};
                Ok(z::Iter::new(BufReader::new(file), fish_path))
            }}
        }}
        #[doc = " Mirrors z.lua's path logic:"]
        #[doc = ""]
        #[doc = " ```lua"]
        #[doc = " DATA_FILE = '~/.zlua'    -- default"]
        #[doc = ""]
        #[doc = " -- in z_init():"]
        #[doc = " local _zl_data = os.getenv('_ZL_DATA')"]
        #[doc = " if _zl_data ~= nil and _zl_data ~= \\"\\" then"]
        #[doc = "     if windows then"]
        #[doc = "         DATA_FILE = _zl_data"]
        #[doc = "     else"]
        #[doc = "         -- avoid windows environments affect cygwin & msys"]
        #[doc = "         if not string.match(_zl_data, '^%a:[/\\\\\\\\]') then"]
        #[doc = "             DATA_FILE = _zl_data"]
        #[doc = "         end"]
        #[doc = "     end"]
        #[doc = " end"]
        #[doc = " ```"]
        fn data_path() -> Result<PathBuf> {{
            if let Some(path) = env::var_os("_ZL_DATA")
                .filter(|path| !path.is_empty())
                .filter(|path| cfg!(target_os = "windows") || !looks_like_windows_path(path))
            {{
                return Ok(PathBuf::from(path));
            }}
            let mut path = dirs::home_dir().context("could not find home directory")?;
            path.push(".zlua");
            Ok(path)
        }}
        #[doc = " Mirrors z.lua's path logic on Fish:"]
        #[doc = ""]
        #[doc = " ```fish"]
        #[doc = " if test -z \\"$XDG_DATA_HOME\\""]
        #[doc = "     set -U _ZL_DATA_DIR \\"$HOME/.local/share/zlua\\""]
        #[doc = " else"]
        #[doc = "     set -U _ZL_DATA_DIR \\"$XDG_DATA_HOME/zlua\\""]
        #[doc = " end"]
        #[doc = " set -x _ZL_DATA \\"$_ZL_DATA_DIR/zlua.txt\\""]
        #[doc = " ```"]
        fn data_path_fish() -> Result<PathBuf> {{
            let mut path = match env::var_os("XDG_DATA_HOME") {{
                Some(xdg) => PathBuf::from(xdg),
                None => {{
                    let mut path = dirs::home_dir().context("could not find home directory")?;
                    path.push(".local");
                    path.push("share");
                    path
                }}
            }};
            path.push("zlua");
            path.push("zlua.txt");
            Ok(path)
        }}
        #[doc = " Matches Lua's `^%a:[/\\\\\\\\]` — ASCII letter, colon, slash-or-backslash."]
        fn looks_like_windows_path(s: &OsStr) -> bool {{
            let bytes = s.as_encoded_bytes();
            bytes.len() >= 3
                && bytes[0].is_ascii_alphabetic()
                && bytes[1] == b':'
                && (bytes[2] == b'/' || bytes[2] == b'\\\\')
        }}
    }}
    mod zsh_z {{
        use crate::db::Dir;
        use crate::import::{{ImportError, Importer, z}};
        use anyhow::{{Context, Result}};
        use std::env;
        use std::fs::File;
        use std::io::BufReader;
        use std::path::PathBuf;
        #[derive(clap :: Args, Clone, Debug)]
        pub(crate) struct ZshZ {{}}
        impl Importer for ZshZ {{
            fn dirs(&self) -> Result<impl Iterator<Item = Result<Dir<'static>, ImportError>>> {{
                let path = data_path()?;
                let file = File::open(&path).with_context(|| format!("could not read {{path:?}}"))?;
                let reader = BufReader::new(file);
                Ok(z::Iter::new(reader, path))
            }}
        }}
        #[doc = " Mirrors zsh-z's path logic:"]
        #[doc = ""]
        #[doc = " ```sh"]
        #[doc = " # Allow the user to specify a custom datafile in $ZSHZ_DATA (or legacy $_Z_DATA)"]
        #[doc = " local custom_datafile=\\"${{ZSHZ_DATA:-$_Z_DATA}}\\""]
        #[doc = " # If the user specified a datafile, use that or default to ~/.z"]
        #[doc = " local datafile=${{${{custom_datafile:-$HOME/.z}}:A}}"]
        #[doc = " ```"]
        fn data_path() -> Result<PathBuf> {{
            match env::var_os("ZSHZ_DATA").or_else(|| env::var_os("_Z_DATA")) {{
                Some(path) => Ok(PathBuf::from(path)),
                None => {{
                    let mut path = dirs::home_dir().context("could not find home directory")?;
                    path.push(".z");
                    Ok(path)
                }}
            }}
        }}
    }}
    use crate::config;
    use crate::db::{{Database, Dir}};
    use anyhow::Result;
    use std::io::{{self, Write}};
    use std::path::PathBuf;
    pub(crate) trait Importer {{
        #[doc = " Yields directory entries to be imported."]
        #[doc = ""]
        #[doc = " The outer `Result` reports failure to fetch the input (e.g. missing"]
        #[doc = " file, subprocess errored). The per-item `Result` reports a malformed"]
        #[doc = " row, which doesn't necessarily abort the whole import."]
        fn dirs(&self) -> Result<impl Iterator<Item = Result<Dir<'static>, ImportError>>>;
    }}
    #[doc = " A single record that failed to import."]
    #[derive(Debug)]
    pub(crate) struct ImportError {{
        #[doc = " Path of the source file containing the offending record. `None` if the"]
        #[doc = " importer is not file-based (e.g. atuin streams from a subprocess)."]
        pub path: Option<PathBuf>,
        #[doc = " 1-indexed line number of the offending input."]
        pub line_num: usize,
        #[doc = " Underlying reason the record could not be imported."]
        pub source: anyhow::Error,
    }}
    #[doc = " Drives a single importer end-to-end: writes each `Ok` dir into the"]
    #[doc = " database and prints each `Err` to stderr in `<path>:<line>: <reason>`"]
    #[doc = " format. Doesn't abort on per-record errors — bad rows are skipped, the"]
    #[doc = " rest of the import continues. After the iteration completes successfully,"]
    #[doc = " the database is deduplicated and aged."]
    pub(crate) fn run(importer: &impl Importer, db: &mut Database) -> Result<()> {{
        let exclude_dirs = config::exclude_dirs()?;
        let stderr = io::stderr();
        let mut stderr = stderr.lock();
        for entry in importer.dirs()? {{
            match entry {{
                Ok(dir) => {{
                    if exclude_dirs.iter().any(|glob| glob.matches(&dir.path)) {{
                        continue;
                    }}
                    db.add_unchecked(dir.path, dir.rank, dir.last_accessed);
                }}
                Err(e) => {{
                    let location = match &e.path {{
                        Some(path) => format!("{{}}:{{}}", path.display(), e.line_num),
                        None => format!("line {{}}", e.line_num),
                    }};
                    _ = writeln!(stderr, "{{location}}: {{:#}}", e.source);
                }}
            }}
        }}
        if db.dirty() {{
            db.dedup();
            let max_age = config::maxage()?;
            db.age(max_age);
        }}
        Ok(())
    }}
}}
mod shell {{
    use crate::cmd::InitHook;
    #[derive(Debug, Eq, PartialEq)]
    pub struct Opts<'a> {{
        pub cmd: Option<&'a str>,
        pub hook: InitHook,
        pub echo: bool,
        pub resolve_symlinks: bool,
    }}
    macro_rules! make_template {{
        ($ name : ident , $ path : expr) => {{
            #[derive(:: std :: fmt :: Debug, :: askama :: Template)]
            # [template (path = $path)]
            pub struct $name<'a>(pub &'a self::Opts<'a>);
            impl<'a> ::std::ops::Deref for $name<'a> {{
                type Target = self::Opts<'a>;
                fn deref(&self) -> &Self::Target {{
                    self.0
                }}
            }}
        }};
    }}
    #[cfg(test)]
    mod tests {{
        use super::*;
        use askama::Template;
        use assert_cmd::Command;
        use rstest::rstest;
        use rstest_reuse::{{apply, template}};
        #[template]
        #[rstest]
        fn opts(
            #[values(None, Some("z"))] cmd: Option<&str>,
            #[values(InitHook::None, InitHook::Prompt, InitHook::Pwd)] hook: InitHook,
            #[values(false, true)] echo: bool,
            #[values(false, true)] resolve_symlinks: bool,
        ) {{
        }}
        #[apply(opts)]
        fn bash_bash(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Bash(&opts).render().unwrap();
            Command::new("bash")
                .args(["--noprofile", "--norc", "-e", "-u", "-o", "pipefail", "-c", &source])
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn bash_shellcheck(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Bash(&opts).render().unwrap();
            Command::new("shellcheck")
                .args(["--enable=all", "-"])
                .write_stdin(source)
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn bash_shfmt(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let mut source = Bash(&opts).render().unwrap();
            source.push('\\n');
            Command::new("shfmt")
                .args(["--diff", "--indent=4", "--language-dialect=bash", "--simplify", "-"])
                .write_stdin(source)
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn elvish_elvish(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let mut source = String::new();
            for line in
                Elvish(&opts).render().unwrap().lines().filter(|line| !line.contains("edit:"))
            {{
                source.push_str(line);
                source.push('\\n');
            }}
            Command::new("elvish")
                .args(["-c", &source, "-norc"])
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn fish_no_builtin_abbr(
            cmd: Option<&str>,
            hook: InitHook,
            echo: bool,
            resolve_symlinks: bool,
        ) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Fish(&opts).render().unwrap();
            assert!(
                !source.contains("builtin abbr"),
                "`builtin abbr` does not work on older versions of Fish"
            );
        }}
        #[apply(opts)]
        fn fish_fish(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Fish(&opts).render().unwrap();
            let tempdir = tempfile::tempdir().unwrap();
            let tempdir = tempdir.path().to_str().unwrap();
            Command::new("fish")
                .env("HOME", tempdir)
                .args(["--command", &source, "--no-config", "--private"])
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn fish_fishindent(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let mut source = Fish(&opts).render().unwrap();
            source.push('\\n');
            let tempdir = tempfile::tempdir().unwrap();
            let tempdir = tempdir.path().to_str().unwrap();
            Command::new("fish_indent")
                .env("HOME", tempdir)
                .write_stdin(source.to_string())
                .assert()
                .success()
                .stdout(source)
                .stderr("");
        }}
        #[apply(opts)]
        fn nushell_nushell(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Nushell(&opts).render().unwrap();
            let tempdir = tempfile::tempdir().unwrap();
            let tempdir = tempdir.path();
            let assert = Command::new("nu")
                .env("HOME", tempdir)
                .args(["--commands", &source])
                .assert()
                .success()
                .stderr("");
            if opts.hook != InitHook::Pwd {{
                assert.stdout("");
            }}
        }}
        #[apply(opts)]
        fn posix_bash(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Posix(&opts).render().unwrap();
            let assert = Command::new("bash")
                .args([
                    "--posix",
                    "--noprofile",
                    "--norc",
                    "-e",
                    "-u",
                    "-o",
                    "pipefail",
                    "-c",
                    &source,
                ])
                .assert()
                .success()
                .stderr("");
            if opts.hook != InitHook::Pwd {{
                assert.stdout("");
            }}
        }}
        #[apply(opts)]
        fn posix_dash(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Posix(&opts).render().unwrap();
            let assert = Command::new("dash")
                .args(["-e", "-u", "-c", &source])
                .assert()
                .success()
                .stderr("");
            if opts.hook != InitHook::Pwd {{
                assert.stdout("");
            }}
        }}
        #[apply(opts)]
        fn posix_shellcheck(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Posix(&opts).render().unwrap();
            Command::new("shellcheck")
                .args(["--enable=all", "-"])
                .write_stdin(source)
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn posix_shfmt(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let mut source = Posix(&opts).render().unwrap();
            source.push('\\n');
            Command::new("shfmt")
                .args(["--diff", "--indent=4", "--language-dialect=posix", "--simplify", "-"])
                .write_stdin(source)
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn powershell_pwsh(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let mut source = "Set-StrictMode -Version latest\\n".to_string();
            Powershell(&opts).render_into(&mut source).unwrap();
            Command::new("pwsh")
                .args(["-NoLogo", "-NonInteractive", "-NoProfile", "-Command", &source])
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn tcsh_tcsh(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Tcsh(&opts).render().unwrap();
            Command::new("tcsh")
                .args(["-e", "-f", "-s"])
                .write_stdin(source)
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn xonsh_black(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let mut source = Xonsh(&opts).render().unwrap();
            source.push('\\n');
            Command::new("black")
                .args(["--check", "--diff", "-"])
                .write_stdin(source)
                .assert()
                .success()
                .stdout("");
        }}
        #[apply(opts)]
        fn xonsh_mypy(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Xonsh(&opts).render().unwrap();
            Command::new("mypy")
                .args(["--command", &source, "--strict"])
                .assert()
                .success()
                .stderr("");
        }}
        #[apply(opts)]
        fn xonsh_pylint(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let mut source = Xonsh(&opts).render().unwrap();
            source.push('\\n');
            Command::new("pylint")
                .args(["--from-stdin", "--persistent=n", "zoxide"])
                .write_stdin(source)
                .assert()
                .success()
                .stderr("");
        }}
        #[apply(opts)]
        fn xonsh_xonsh(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Xonsh(&opts).render().unwrap();
            let tempdir = tempfile::tempdir().unwrap();
            let tempdir = tempdir.path().to_str().unwrap();
            Command::new("xonsh")
                .args(["-c", &source, "--no-rc"])
                .env("HOME", tempdir)
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn zsh_shellcheck(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Zsh(&opts).render().unwrap();
            Command::new("shellcheck")
                .args(["--enable=all", "-"])
                .write_stdin(source)
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
        #[apply(opts)]
        fn zsh_zsh(cmd: Option<&str>, hook: InitHook, echo: bool, resolve_symlinks: bool) {{
            let opts = Opts {{ cmd, hook, echo, resolve_symlinks }};
            let source = Zsh(&opts).render().unwrap();
            Command::new("zsh")
                .args(["-e", "-u", "-o", "pipefail", "--no-globalrcs", "--no-rcs", "-c", &source])
                .assert()
                .success()
                .stdout("")
                .stderr("");
        }}
    }}
}}
mod util {{
    use crate::db::{{Dir, Epoch}};
    use crate::error::SilentExit;
    #[cfg(windows)]
    use anyhow::anyhow;
    use anyhow::{{Context, Result, bail}};
    use std::ffi::OsStr;
    use std::fs::{{self, File, OpenOptions}};
    use std::io::{{self, Read, Write}};
    use std::path::{{Component, Path, PathBuf}};
    use std::process::{{Child, Command, Stdio}};
    use std::time::SystemTime;
    use std::{{env, mem}};
    pub const SECOND: Epoch = 1;
    pub const MINUTE: Epoch = 60 * SECOND;
    pub const HOUR: Epoch = 60 * MINUTE;
    pub const DAY: Epoch = 24 * HOUR;
    pub const WEEK: Epoch = 7 * DAY;
    pub const MONTH: Epoch = 30 * DAY;
    pub struct Fzf(Command);
    impl Fzf {{
        const ERR_FZF_NOT_FOUND: &'static str = "could not find fzf, is it installed?";
        pub fn new() -> Result<Self> {{
            #[cfg(windows)]
            let program = which::which("fzf.exe").map_err(|_| anyhow!(Self::ERR_FZF_NOT_FOUND))?;
            #[cfg(not(windows))]
            let program = "fzf";
            let mut cmd = Command::new(program);
            cmd.args(["--delimiter=\\t", "--nth=2", "--read0"])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped());
            Ok(Fzf(cmd))
        }}
        pub fn enable_preview(&mut self) -> &mut Self {{
            if !cfg!(unix) {{
                return self;
            }}
            self.args([
                if cfg!(target_os = "linux") {{
                    r"--preview=\\command -p ls -Cp --color=always --group-directories-first {{2..}}"
                }} else {{
                    r"--preview=\\command -p ls -Cp {{2..}}"
                }},
                "--preview-window=down,30%,sharp",
            ])
            .envs([("CLICOLOR", "1"), ("CLICOLOR_FORCE", "1"), ("SHELL", "sh")])
        }}
        pub fn args<I, S>(&mut self, args: I) -> &mut Self
        where
            I: IntoIterator<Item = S>,
            S: AsRef<OsStr>,
        {{
            self.0.args(args);
            self
        }}
        pub fn env<K, V>(&mut self, key: K, val: V) -> &mut Self
        where
            K: AsRef<OsStr>,
            V: AsRef<OsStr>,
        {{
            self.0.env(key, val);
            self
        }}
        pub fn envs<I, K, V>(&mut self, vars: I) -> &mut Self
        where
            I: IntoIterator<Item = (K, V)>,
            K: AsRef<OsStr>,
            V: AsRef<OsStr>,
        {{
            self.0.envs(vars);
            self
        }}
        pub fn spawn(&mut self) -> Result<FzfChild> {{
            match self.0.spawn() {{
                Ok(child) => Ok(FzfChild(child)),
                Err(e) if e.kind() == io::ErrorKind::NotFound => bail!(Self::ERR_FZF_NOT_FOUND),
                Err(e) => Err(e).context("could not launch fzf"),
            }}
        }}
    }}
    pub struct FzfChild(Child);
    impl FzfChild {{
        pub fn write(&mut self, dir: &Dir, now: Epoch) -> Result<Option<String>> {{
            let handle = self.0.stdin.as_mut().unwrap();
            match write!(handle, "{{}}\\0", dir.display().with_score(now).with_separator('\\t')) {{
                Ok(()) => Ok(None),
                Err(e) if e.kind() == io::ErrorKind::BrokenPipe => self.wait().map(Some),
                Err(e) => Err(e).context("could not write to fzf"),
            }}
        }}
        pub fn wait(&mut self) -> Result<String> {{
            mem::drop(self.0.stdin.take());
            let mut stdout = self.0.stdout.take().unwrap();
            let mut output = String::new();
            stdout.read_to_string(&mut output).context("failed to read from fzf")?;
            let status = self.0.wait().context("wait failed on fzf")?;
            match status.code() {{
                Some(0) => Ok(output),
                Some(1) => bail!("no match found"),
                Some(2) => bail!("fzf returned an error"),
                Some(130) => bail!(SilentExit {{ code: 130 }}),
                Some(128..=254) | None => bail!("fzf was terminated"),
                _ => bail!("fzf returned an unknown error"),
            }}
        }}
    }}
    #[doc = " Similar to [`fs::write`], but atomic (best effort on Windows)."]
    pub fn write(path: impl AsRef<Path>, contents: impl AsRef<[u8]>) -> Result<()> {{
        let path = path.as_ref();
        let contents = contents.as_ref();
        let dir = path.parent().unwrap();
        let (mut tmp_file, tmp_path) = tmpfile(dir)?;
        let result = (|| {{
            _ = tmp_file.set_len(contents.len() as u64);
            tmp_file
                .write_all(contents)
                .with_context(|| format!("could not write to file: {{}}", tmp_path.display()))?;
            #[cfg(unix)]
            if let Ok(metadata) = path.metadata() {{
                use std::os::unix::fs::{{MetadataExt, fchown}};
                _ = fchown(&tmp_file, Some(metadata.uid()), Some(metadata.gid()));
            }}
            tmp_file.sync_all().with_context(|| {{
                format!("could not sync writes to file: {{}}", tmp_path.display())
            }})?;
            mem::drop(tmp_file);
            rename(&tmp_path, path)
        }})();
        if result.is_err() {{
            _ = fs::remove_file(&tmp_path);
        }}
        result
    }}
    #[doc = " Atomically create a tmpfile in the given directory."]
    fn tmpfile(dir: impl AsRef<Path>) -> Result<(File, PathBuf)> {{
        const MAX_ATTEMPTS: usize = 5;
        const TMP_NAME_LEN: usize = 16;
        let dir = dir.as_ref();
        let mut attempts = 0;
        loop {{
            attempts += 1;
            let mut name = String::with_capacity(TMP_NAME_LEN);
            name.push_str("tmp_");
            while name.len() < TMP_NAME_LEN {{
                name.push(fastrand::alphanumeric());
            }}
            let path = dir.join(name);
            match OpenOptions::new().write(true).create_new(true).open(&path) {{
                Ok(file) => break Ok((file, path)),
                Err(e) if e.kind() == io::ErrorKind::AlreadyExists && attempts < MAX_ATTEMPTS => {{}}
                Err(e) => {{
                    break Err(e)
                        .with_context(|| format!("could not create file: {{}}", path.display()));
                }}
            }}
        }}
    }}
    #[doc = " Similar to [`fs::rename`], but with retries on Windows."]
    fn rename(from: impl AsRef<Path>, to: impl AsRef<Path>) -> Result<()> {{
        let from = from.as_ref();
        let to = to.as_ref();
        const MAX_ATTEMPTS: usize = if cfg!(windows) {{ 5 }} else {{ 1 }};
        let mut attempts = 0;
        loop {{
            match fs::rename(from, to) {{
                Err(e)
                    if e.kind() == io::ErrorKind::PermissionDenied && attempts < MAX_ATTEMPTS =>
                {{
                    attempts += 1
                }}
                result => {{
                    break result.with_context(|| {{
                        format!("could not rename file: {{}} -> {{}}", from.display(), to.display())
                    }});
                }}
            }}
        }}
    }}
    pub fn canonicalize(path: impl AsRef<Path>) -> Result<PathBuf> {{
        dunce::canonicalize(&path)
            .with_context(|| format!("could not resolve path: {{}}", path.as_ref().display()))
    }}
    pub fn current_dir() -> Result<PathBuf> {{
        env::current_dir().context("could not get current directory")
    }}
    pub fn current_time() -> Result<Epoch> {{
        let current_time = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .context("system clock set to invalid time")?
            .as_secs();
        Ok(current_time)
    }}
    pub fn path_to_str(path: &impl AsRef<Path>) -> Result<&str> {{
        let path = path.as_ref();
        path.to_str().with_context(|| format!("invalid unicode in path: {{}}", path.display()))
    }}
    #[doc = " Returns the absolute version of a path. Like"]
    #[doc = " [`std::path::Path::canonicalize`], but doesn't resolve symlinks."]
    pub fn resolve_path(path: impl AsRef<Path>) -> Result<PathBuf> {{
        let path = path.as_ref();
        let base_path;
        let mut components = path.components().peekable();
        let mut stack = Vec::new();
        if cfg!(windows) {{
            use std::path::Prefix;
            fn get_drive_letter(path: impl AsRef<Path>) -> Option<u8> {{
                let path = path.as_ref();
                let mut components = path.components();
                match components.next() {{
                    Some(Component::Prefix(prefix)) => match prefix.kind() {{
                        Prefix::Disk(drive_letter) | Prefix::VerbatimDisk(drive_letter) => {{
                            Some(drive_letter)
                        }}
                        _ => None,
                    }},
                    _ => None,
                }}
            }}
            fn get_drive_path(drive_letter: u8) -> PathBuf {{
                format!(r"{{}}:\\", drive_letter as char).into()
            }}
            fn get_drive_relative(drive_letter: u8) -> Result<PathBuf> {{
                let path = current_dir()?;
                if Some(drive_letter) == get_drive_letter(&path) {{
                    return Ok(path);
                }}
                if let Some(path) = env::var_os(format!("={{}}:", drive_letter as char)) {{
                    return Ok(path.into());
                }}
                let path = get_drive_path(drive_letter);
                Ok(path)
            }}
            match components.peek() {{
                Some(Component::Prefix(prefix)) => match prefix.kind() {{
                    Prefix::Disk(drive_letter) => {{
                        let disk = components.next().unwrap();
                        if components.peek() == Some(&Component::RootDir) {{
                            let root = components.next().unwrap();
                            stack.push(disk);
                            stack.push(root);
                        }} else {{
                            base_path = get_drive_relative(drive_letter)?;
                            stack.extend(base_path.components());
                        }}
                    }}
                    Prefix::VerbatimDisk(drive_letter) => {{
                        components.next();
                        if components.peek() == Some(&Component::RootDir) {{
                            components.next();
                        }}
                        base_path = get_drive_path(drive_letter);
                        stack.extend(base_path.components());
                    }}
                    _ => bail!("invalid path: {{}}", path.display()),
                }},
                Some(Component::RootDir) => {{
                    components.next();
                    let current_dir = env::current_dir()?;
                    let drive_letter = get_drive_letter(&current_dir).with_context(|| {{
                        format!("could not get drive letter: {{}}", current_dir.display())
                    }})?;
                    base_path = get_drive_path(drive_letter);
                    stack.extend(base_path.components());
                }}
                _ => {{
                    base_path = current_dir()?;
                    stack.extend(base_path.components());
                }}
            }}
        }} else if components.peek() == Some(&Component::RootDir) {{
            let root = components.next().unwrap();
            stack.push(root);
        }} else {{
            base_path = current_dir()?;
            stack.extend(base_path.components());
        }}
        for component in components {{
            match component {{
                Component::Normal(_) => stack.push(component),
                Component::CurDir => {{}}
                Component::ParentDir => {{
                    if stack.last() != Some(&Component::RootDir) {{
                        stack.pop();
                    }}
                }}
                Component::Prefix(_) | Component::RootDir => unreachable!(),
            }}
        }}
        Ok(stack.iter().collect())
    }}
    #[doc = " Convert a string to lowercase, with a fast path for ASCII strings."]
    pub fn to_lowercase(s: impl AsRef<str>) -> String {{
        let s = s.as_ref();
        if s.is_ascii() {{ s.to_ascii_lowercase() }} else {{ s.to_lowercase() }}
    }}
}}
pub fn main() -> ExitCode {{
    unsafe {{ env::remove_var("RUST_LIB_BACKTRACE") }};
    unsafe {{ env::remove_var("RUST_BACKTRACE") }};
    {template}
    
    match Cmd::parse().run() {{
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => match e.downcast::<SilentExit>() {{
            Ok(SilentExit {{ code }}) => code.into(),
            Err(e) => {{
                _ = writeln!(io::stderr(), "zoxide: {{e:?}}");
                ExitCode::FAILURE
            }}
        }},
    }}
}}


"""