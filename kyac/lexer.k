
class Lexer {

	File file;

	String buffer = "";
	int line_number = 0;
	int last_index = -1;

	public Lexer(File file) { // line 10
		this.file = file;
	}

	public String operator: () {
		// Iterator
		return get_next_token();
	}

	private String _raw_next_token() {
		while (buffer.length() == 0 || buffer.isspace()) {
			buffer = file.readline();
			line_no++;
			if (buffer.length() == 0) {
				last_index = -1;
				return null;
			}

			buffer.strip();
		}

		String tmp = "";
		bool instr = false;
		bool inch = false;
		for (int i = 0; i < buffer.length(); i++) {
			char c = buffer[i];
			if (instr) {
				// process string stuff
				tmp += c;
				if (c == '"') {
					instr = false;
					break;
				}
			} else if (inch) {
				// process char stuff
				tmp += c;
				if (c == '\'') {
					inch = false;
					break;
				}
			} else {
				if (isspace(c)) {
					if (tmp.length() > 0) {
						continue;
					} else {
						break;
					}
				} else if (is_token_char(c)) {
					if (tmp.length() > 0) {
						i--;
						break;
					}
					if (i + 1 < buffer.length()) {
						String op_test = c + buffer[i + 1];
						if (is_dualop(op_test)) {
							tmp = op_test;
							i++;
							break;
						}
						tmp = c;
						break;
					}
				} else if (c == '"') {
					instr = true;
					tmp += c;
				} else if (c == '\'') {
					inch = true;
					tmp += c;
				} else {
					tmp += c;
				}
			}
		}

		last_index = i;
		return tmp;
		
	}

	public String get_next_token() {
		String token;

		token = _raw_next_token();

		if (last_index > 0) {
			buffer = buffer.substring(last_index);
		}

		return token;
	}

	public String peek_next_token() {
		String token = _raw_next_token();

		return token;
	}
}
