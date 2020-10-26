
import fileio;

import .lexer;
import .parser;
import .language;

// This class combines the functionality of the lexer, parser, code accumulator, compilation, and optimization.
class CodeBuilder {

	CodeAccumulator code_accumulator;
	Lexer lexer;
	Parser parser;

	public CodeBuilder(String filename) {
		lexer = Lexer(fopen(filename, "r"));
		parser = Parser(lexer);
		code_accumulator = CodeAccumulator();
	}

	private CodeBuilder(CodeAccumulator accumulator, String filename) {
		lexer = Lexer(fopen(filename, "r"));
		parser = Parser(lexer);

		code_accumulator = accumulator;
	}

	public int accumulate() {
		// This function puts all the code from all imported files together
		// It does not compile it, however.

		int exit_code = 0;

		// A toplevel is a block like this class, an import statement, a function, etc
		for (Toplevel toplevel: parser) {
			if (!code_accumulator.add_toplevel(toplevel)) {
				exit_code = -1;
			}
		}

		return exit_code;
	}
}

void main(String[] argv) {
	if (argv.length() != 2) {
		if (argv.length() == 0)
			println("Warning: problem detected in execution environment: argv.length() is 0.\n Usage: kyac [filename]");
		else
			println("Usage: " + argv[0] + " [filename]");

		println("Needed files will automatically be added.");
		exit(100);
	}
	
}
