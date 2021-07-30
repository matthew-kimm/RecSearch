class SharedTestSplitter:
    def compare_dict_dataframes(self, dict1, dict2):
        if set(dict1.keys()) == set(dict2.keys()):
            compare = {key: dict1[key].equals(dict2[key]) for key in dict1.keys() if key in dict2.keys()}
            return all(compare.values())
        else:
            raise KeyError('Keys in dictionaries do not match')
