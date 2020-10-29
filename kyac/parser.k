
import fileio;

import .language;

class Parser {

	Lexer lexy;

	int last_line_start = 0;

	public Parser(Lexer lex) {
		lexy = lex;
	}

	private void syntax_error(String message) {
		println("Syntax error lines " + last_line_start + " - " + lexy.get_line_number() + ": " + message);
	}

	public Toplevel operator: () {

		Toplevel toplevel = null;

		while (toplevel == null) {
			String token = lexy.get_next_token();

			if (token == null)
				return null;

			if (token == "import") {
				toplevel = parse_import();
			} else if (token == "mutable" || token == "abstract") {
				bool is_mutable = token == "mutable";
				bool is_abstract = token == "abstract";

				String token = lexy.get_next_token();
				if (token == "mutable") {
					is_mutable = true;
					
				} else if (token == "abstract")
					is_abstract = true;
				
				if (token != "class")
					syntax_error("Unexpected token in class definition '" + token + "'");
			}
		}
	}

	Toplevel parse_import() {
		String first_token = lexy.get_next_token();

		if (first_token == ";") {
			syntax_error("Empty import");
			return null;
		}

		String path = "";

		if (first_token == ".")
			path = "./";
		else
			path = first_token;

		String token = "";
		while (true) {
			token = lexy.get_next_token();

			if (token == ";") {
				if (path.endswith("/")) {
					syntax_error("Import ends with '.;'");
					return null;
				}

				return Import(path);
			} else if (token == ".") {
				path += '/';
			} else
				path += token;
		}
	}
}
