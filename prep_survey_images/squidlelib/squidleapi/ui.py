from pick import pick
import json
import pprint


class UIComponents(object):
    @staticmethod
    def select_list(title, optionlist, multi_select=False, min_selection_count=1):
        if not multi_select:
            option, index = pick(optionlist, title, multi_select=False, min_selection_count=min_selection_count)
            return option
        else:
            options = pick(optionlist, title, multi_select=True, min_selection_count=min_selection_count)
            return [o[0] for o in options]

    @staticmethod
    def input_json(title):
        print ("\n{}. \nPaste JSON below. Hit ENTER, then CTRL-D to save.\n".format(title))
        contents = []
        while True:
            try:
                line = raw_input("")
            except EOFError:
                break
            contents.append(line)
        return json.loads("\n".join(contents))

    @staticmethod
    def input_multi(title, fields):
        if isinstance(fields, list):
            fields = {f: None for f in fields}  # convert to dict
        print (title)
        for f in fields.keys():
            if fields[f] is not None:
                if isinstance(fields[f], basestring):
                    print ("\n'{}' is currently set to:\n{}\n".format(f, fields[f]))
                    fields[f] = raw_input("New value for '{}' (ENTER to skip):".format(f)) or fields[f]
                elif isinstance(fields[f], dict) or isinstance(fields[f], list):
                    print ("\n'{}' is currently set to:\n{}\n".format(f, json.dumps(fields[f], indent=2)))
                    fields[f] = UIComponents.input_json("New value for '{}'  (ENTER to skip)".format(f)) or fields[f]
                else:
                    raise Exception("Unsupported field type for '{}'. Don't know how to handle type: {}.".format(f, type(fields[f])))
            else:
                fields[f] = raw_input("New value for '{}':".format(f))
        return fields