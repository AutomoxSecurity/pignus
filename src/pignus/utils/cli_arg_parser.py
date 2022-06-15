"""Cli Arg Parser

Testing
Unit Tests at automox/pignus/tests/unit/utils/test_cli_arg_parser.py

"""

from rich import print


class CliArgParser:
    def __init__(
            self,
            raw_args: str,
            verbs: list = [],
            subjects: list = [],
            options: dict = {}):
        """Set the positional args and optional args.
        Args:
            verbs:      A list of all supported actions to take, such as ex: ["get", "create"]
            subjects:   A list
        :unit-test: TestCliArgParser.test____init__
        """
        self.raw_args = raw_args
        self.verbs = verbs
        self.subjects = subjects
        self.options = options
        self.route_options = {}
        self.cli_args = {
            "verb": None,
            "subject": None,
            "options": {},
        }
        self.help_menu_text = "Help menu not yet set"
        self.errors = {}

    def parse(self) -> dict:
        """Parse args from the CLI.
        :unit-test: TestCliArgParser.test__parse
        """
        self.cli_args["verb"] = self._get_verb()
        self.cli_args["subject"] = self._get_subject()
        self.cli_args["value"] = self._get_value()
        self.cli_args["options"] = self._get_options()
        self.cli_args["errors"] = self.errors

        # if self.cli_args["errors"]:
        #     print(self.cli_args["errors"])
        #     self.help_menu()
        #     exit(1)

        self._set_option_defaults()

        if self.show_help():
            self.help_menu()
            exit()

        return self.cli_args

    def get_subject(self):
        return self._get_subject()

    def _get_verb(self) -> str:
        """Get the verb of the CLI request, typically the first argument.
        :unit-test: TestCliArgParser.test___get_verb
        """

        if len(self.raw_args) < 1:
            self.errors["verb"] = "A verb is required."
            return False

        verb = self.raw_args[0]
        if verb not in self.verbs:
            self.errors["verb"] = "Uknown verb."
            return False

        return verb

    def _get_subject(self) -> str:
        """Get the subject of the CLI argument.
        :unit-test: TestCliArgParser.test___get_subject
        """
        if len(self.raw_args) < 2:
            self.errors["subject"] = "No subject found."
            return False

        subject = self.raw_args[1]
        if self.raw_args[1] not in self.subjects:
            self.errors["subject"] = "Uknown subject."
            return False

        return subject

    def _get_value(self) -> str:
        """Get the value of a CLI request.
        :unit-test: TestCliArgParser.test___get_value
        """
        if len(self.raw_args) < 3:
            return False
        the_args = self.raw_args[2:]
        for a_arg in the_args:
            if self._is_option(a_arg):
                continue
            return a_arg
        return False

    def _get_options(self) -> dict:
        """Get the options of a CLI request.
        :unit-test: TestCliArgParser.test___get_options
        """
        options = {}
        count = 0
        skip_next = False
        for the_arg in self.raw_args:
            count += 1
            if not self._is_option(the_arg):
                continue

            if skip_next:
                skip_next = False
                count += 1
                continue
            stripped = self._strip_option(the_arg)
            original_arg = stripped["original_arg"]
            arg_value = stripped["value"]

            option_name = self._match_option(original_arg)

            if not option_name:
                self.errors["options"] = "Could not parse option %s" % original_arg
                continue

            # Get the option value if we dont already
            option_type = self._get_option_type(option_name)
            if option_type == "dict":
                arg_value = self._get_option_dict_value(count)
                skip_next = True
            elif option_type == "bool":
                arg_value = True

            # if the option doesnt have a value
            elif not arg_value and len(self.raw_args) > count:
                arg_value = self.raw_args[count]
                skip_next = True

            options[option_name] = arg_value

        return options

    def show_help(self) -> bool:
        """Determine if the help menu should be shown.
        :unit-test: TestCliArgParser.test__show_help
        """
        show_help = False
        return False
        for arg_name, arg_info in self.cli_args.items():

            if arg_name == "options":
                continue

            if arg_name == "help":
                show_help = True
                break

        for option_name, option_value in self.cli_args["options"].items():
            if option_name in ["help", "h"]:
                show_help = True
                break
        return show_help

    def help_menu(self):
        """Display the help menu."""
        print(self.help_menu_text)
        return True

    # def _get_option_and_value(self, raw_arg: str, next_arg: str = None) -> tuple:
    #     """Pull the option name and value, expanding the option name to its root."""
    #     if "=" in raw_arg:
    #         arg_split = raw_arg.split("=")
    #         arg_name = arg_split[0].replace("-", "")
    #         arg_value = arg_split[1]
    #     else:
    #         arg_name = raw_arg.replace("-", "")
    #         if not next_arg:
    #             arg_value = None
    #         elif next_arg[0] == "-":
    #             arg_value = None
    #         else:
    #             arg_value = next_arg

    #     # Map the option name to its root
    #     for arg_map_name, arg_map_values in self.options.items():
    #         for arg_map_value in arg_map_values:
    #             if raw_arg == arg_map_value:
    #                 arg_name = arg_map_name

    #     return arg_name, arg_value

    def _set_option_defaults(self) -> bool:
        """Make sure all option names are represented in the cli_args output, setting to False if
        it does not already have a given value.
        """
        for option_name, option_triggers in self.options.items():
            # if not self.cli_args["options"]:
            #     return False
            if option_name in self.cli_args["options"]:
                if not self.cli_args["options"]:
                    self.cli_args["options"] = True
                continue
            self.cli_args["options"][option_name] = None

        # Add route specific defaults
        route_phrase = "%s %s" % (self.cli_args["verb"], self.cli_args["subject"])
        if route_phrase not in self.route_options:
            return True

        for option_name, option_flags in self.route_options[route_phrase].items():
            if option_name not in self.cli_args["options"]:
                self.cli_args["options"][option_name] = None

        return True

    def _is_option(self, phrase: str) -> bool:
        """Check if a string is being submitted as an option, starting with a - or --.
        :unit-test: TestCliArgParser.test___is_option
        """
        if not phrase:
            return False
        if len(phrase) <= 1:
            return False
        if phrase[0] == "-":
            return True
        return False

    def _strip_option(self, phrase: str) -> dict:
        """Separate the option and potential value from extraneous characters.
        :unit-test: TestCliArgParser.test___is_option
        """
        original_phrase = phrase
        if phrase[:2] == "--":
            phrase = phrase[2:]
        elif phrase[0] == "-":
            phrase = phrase[1:]

        value = None
        if "=" in phrase:
            split = phrase.split("=")
            original_phrase = original_phrase.split("=")[0]
            phrase = split[0]
            value = split[1]

        return {
            "original_arg": original_phrase,
            "arg": phrase,
            "value": value
        }

    def _match_option(self, phrase: str) -> str:
        """Match an phrase such as "--id" with an option registered to the class.
        :unit-test: TestCliArgParser.test___match_option
        """
        for option_name, option_flags in self.options.items():
            if phrase in option_flags:
                return option_name

        # Check the route options for a route specific option.
        if not self.route_options:
            return False

        route_phrase = "%s %s" % (self.cli_args["verb"], self.cli_args["subject"])

        if route_phrase not in self.route_options:
            return False

        for option_name, option_flags in self.route_options[route_phrase].items():
            if phrase in option_flags:
                return option_name

        return False

    def _get_option_type(self, option_name: str) -> str:
        """Get the CLI option type for special options. This is defined in the field values
        preceeded with a "*". Currently supported *type_dict
        :unit-test: TestCliArgParser.test___get_option_type
        """
        if option_name in self.options:
            if "*type_dict" in self.options[option_name]:
                return "dict"
            if "*type_bool" in self.options[option_name]:
                return "bool"

        route_phrase = "%s %s" % (self.cli_args["verb"], self.cli_args["subject"])
        if route_phrase not in self.route_options:
            return None

        if option_name in self.route_options[route_phrase]:
            if "*type_dict" in self.route_options[route_phrase][option_name]:
                return "dict"

        return None

    def _get_option_dict_value(self, count: int) -> dict:
        """Get the value for an option dictionary.
        :unit-test:
        """
        if len(self.raw_args) < count:
            self.errors["option"] = "error"

        raw_value = self.raw_args[count]

        if "," in raw_value:
            values = raw_value.split(",")
        else:
            values = [raw_value]

        ret = {}
        for val in values:
            split = val.split("=")
            ret[split[0]] = split[1]
        return ret

# End File: automox/pignus/src/pignus/utils/cli_arg_parse.py
