from string import printable
from typing import List

from utils import SamplesStatistic


class LzwCoder:
    @staticmethod
    def _get_start_encoding_lexicon() -> dict:
        """
        Generate initial encoding lexicon dictionary (letter: enumerate index)
        for string.printable values
        :return: initial encoding lexicon
        """
        return {letter: index for index, letter in enumerate(printable)}

    @staticmethod
    def _get_start_decoding_lexicon() -> dict:
        """
        Generate initial decoding lexicon dictionary (enumerate index: letter)
        for string.printable values
        :return: initial decoding lexicon
        """
        return {index: letter for index, letter in enumerate(printable)}

    @staticmethod
    def _add_to_encoding_lexicon(lexicon: dict, new_item: str) -> int:
        """
        Generate new unique value for new_item and add it to encoding lexicon,
        as {new_item: unique value}
        :param lexicon: encoding lexicon at the moment
        :param new_item: item, which we should add to lexicon
        :return: Generated unique value, we added
        """
        new_value = max(lexicon.values()) + 1
        lexicon[new_item] = new_value
        return new_value

    @staticmethod
    def _add_to_decoding_lexicon(lexicon: dict, new_value: str) -> str:
        """"
        Generate new unique value for new_value and add it to decoding lexicon,
        as {unique value: new_item}
        :param lexicon: decoding lexicon at the moment
        :param new_value: value, which we should add to lexicon
        :return: value, we added to lexicon
        """
        new_item = max(lexicon.keys()) + 1
        lexicon[new_item] = new_value
        return new_value

    @classmethod
    def encode(cls, text: str) -> List[int]:
        """
        Encode original text with LZW algorithm to list of int numbers
        :param text: original text, we should encode
        :return: encoded text, as list of int numbers
        """
        lexicon = cls._get_start_encoding_lexicon()

        encoded_text = []
        suffix = ''
        for letter in text:
            temp = suffix + letter
            if temp in lexicon:
                suffix = temp
            else:
                encoded_text.append(lexicon.get(suffix))
                cls._add_to_encoding_lexicon(lexicon, temp)
                suffix = letter
        else:
            encoded_text.append(lexicon.get(suffix))

        return encoded_text

    @classmethod
    def decode(cls, encoded_text: List[int]) -> str:
        """
        Decode list of int numbers to original text with LZW algorithm
        :param encoded_text: encoded text, we should decode
        :return: original text
        """
        lexicon = cls._get_start_decoding_lexicon()

        decoded_text = []
        prev_code = encoded_text[0]
        decoded_text.append(lexicon.get(prev_code))
        entry = ''
        for curr_code in encoded_text[1:]:
            if curr_code in lexicon:
                entry = lexicon.get(curr_code)
            else:
                entry = entry + entry[0]
            decoded_text.append(entry)
            last_letter = entry[0]
            new_value = lexicon.get(prev_code) + last_letter
            cls._add_to_decoding_lexicon(lexicon, new_value)
            prev_code = curr_code

        return ''.join(decoded_text)


if __name__ == '__main__':
    origin_sample = 'Testing phrase for Lempel, Ziv and Welch algorithm.'
    lzw = LzwCoder()
    encoded_sample = lzw.encode(origin_sample)
    decoded_sample = lzw.decode(encoded_sample)

    stat = SamplesStatistic(origin_sample, encoded_sample, decoded_sample)
    stat.samples_statistic()
