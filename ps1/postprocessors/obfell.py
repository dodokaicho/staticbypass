import string
import random
import os
import argparse

class obfell:
    def __init__(self, amount_of_arrays = 32, array_name_length = 32, number_of_operations = 1):
        """Initializes ScriptObfuscator

        Args:
            filepath (str): Path to original (non-obfuscated) script
            amount_of_arrays (int): Ammount of randomized arrays to generate
            number_of_operations (int, optional): Amount of operations to subdivide number
        
        Attributes:
            filepath (str): Path to original (non-obfuscated) script
            amount_of_arrays (int): Ammount of randomized arrays to generate
            number_of_operations (int, optional):Amount of operations to subdivide number
            created_arrays (dict[str, list[str]]): Dictionary of all generated randommized arrays
            list_of_chars (list[str]): List of all characters for generating arrays
            original_script (str): Content of original (non-obfuscated) script
        """
        self.amount_of_arrays = amount_of_arrays
        self.array_name_length = array_name_length
        self.number_of_operations = number_of_operations
        self.created_arrays : dict[str, list[str]] = {}
        self.list_of_chars : list[str]= [char for char in string.printable]
        self.original_script : str = ""
      
    def load_file(self) -> bool:
        """Loads the specified file using self.filepath

        Returns:
            bool: False if file not found. True if file content is loaded
            to self.original_script
        """        
        if not os.path.isfile(self.filepath):
            return False
        
        with open(self.filepath) as file:
            self.original_script = file.read()
        
        return True

    def generate_arrays(self) -> None:
        """Generates randomizes arrays of characters and adds them to
        self.created_arrays dictionary
        """        
        for _ in range(self.amount_of_arrays):
            lof_copy : list[str] = self.list_of_chars.copy()
            array_name : str = "".join([random.choice(string.ascii_letters) for i in range(self.array_name_length)])

            random.shuffle(lof_copy)
            
            self.created_arrays[array_name] = lof_copy

    def created_arrays_to_ps_string(self) -> str:
        """Uses self.created_arrays to created a string of all the arrays of characters
        that can be inserted in powershell using [char]n instead of the actual chars

        Example: $bKNRvMCrlnHyKGJhxFQuyBRFkpQQvoRv = ([char](75 + 46),[char](- 59 + 150)...

        Returns:
            str: String off all arrays in Powershell format
        """        
        created_arrays_strings : str = ""
        for name, chars_list in self.created_arrays.items():
            created_arrays_strings += f"${name} = ("
            for char in chars_list:
                created_arrays_strings += f"[char]({self.number_to_arithmetic_expression(ord(char))})"
                if char != chars_list[-1]:
                    created_arrays_strings += ","
            
            created_arrays_strings += ")\n"

        return created_arrays_strings

    def obfuscated_script_code(self) -> str:
        """Grabs the original content of the script and obfuscates it. Separateseach
        character which are joined again using -JOIN, and executed in a string using
        iex

        Example: iex (($hQMaJftoCBzuwZwkQrtYmJDqMvVrmFLM[25 + 22],...) -JOIN "")

        Returns:
            str: obfuscated script code
        """        
        obfuscated_command_string : str = "iex (("

        for char in self.original_script:
            array_name : str = random.choice(list(self.created_arrays.keys()))
            char_index : int = self.created_arrays[array_name].index(char)
            obfuscated_command_string += f"${array_name}[{self.number_to_arithmetic_expression(char_index)}],"

        obfuscated_command_string += ') -JOIN "")'

        return obfuscated_command_string
    
    def generate_obfuscated_powershell_script(self) -> None:
        """Generates the obfuscated version of the original script and stores it as
        an output file called output.ps1
        """        
        arrays : str = self.created_arrays_to_ps_string()
        command : str = self.obfuscated_script_code()

        with open(self.filepath, "w") as obfuscated_output_file:
            obfuscated_output_file.write(arrays)
            obfuscated_output_file.write(command.replace(",) -JOIN", ") -JOIN")) #TO-DO: Find how to eliminate extra, at the end (causes error if left)

    def number_to_arithmetic_expression(self, number: int) -> str:
        """Subdivides a number (character ascii value) into various arithmetic
        operations

        Example (5 operations): [char]120 -> [char](-55 + 37 + 90 - 3 + 80 - 29)

        0 operations results in the number remaining the same

        Args:
            number (int): Number to subdivide

        Returns:
            str: Subdivided number
        """        
        parts : list[str] = []

        for _ in range(self.number_of_operations):
            num  : int= random.randint(10, 99)
            if random.choice([True, False]):
                parts.append(f'+ {num}')
                number -= num
            else:
                parts.append(f'- {num}')
                number += num

        if number > 0:
            parts.append(f'+ {number}')
        elif number < 0:
            parts.append(f'- {-number}')

        expression : str = ' '.join(parts).lstrip('+ ')
        return expression

    def apply(self, filepath):
        self.filepath = filepath

        #If the file is not found, exit script
        if not self.load_file():
            print("File not found")
            return 
        
        self.generate_arrays()
        self.generate_obfuscated_powershell_script()
