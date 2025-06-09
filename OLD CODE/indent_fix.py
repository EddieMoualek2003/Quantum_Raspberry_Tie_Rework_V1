def indent_file_lines(input_path, output_path, indent='\t'):
    try:
        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            for line in infile:
                outfile.write(f"{indent}{line}")
        print(f"Indented file written to: {output_path}")
    except FileNotFoundError:
        print(f"File not found: {input_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
input_file = 'QuantumRaspberryTie.qk1.py'
output_file = 'indented_code.py'
indent_file_lines(input_file, output_file)
