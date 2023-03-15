from typing import List, Tuple

from utils import SamplesStatistic


class BurrowsWheelerTransform:
    @staticmethod
    def shifted_texts(text: str) -> List[str]:
        """
        Generate and return list of shifted on one char versions of text
        :param text: original word, we should shift
        :return: list of shifted on one char strings
        """
        shifted_texts = [text[i:] + text[:i] for i in range(len(text))]
        return shifted_texts

    @staticmethod
    def _calc_origin_index(shifted_texts: List[str], text: str) -> int:
        """
        Find index of original text value in list of shifted versions
        :param shifted_texts: list of shifted versions of text
        :param text: original text
        :return: index of original text value in list
        """
        for ind, item in enumerate(shifted_texts):
            if item == text:
                return ind
        return -1

    @staticmethod
    def _last_letter_text(shifted_texts: List[str]) -> str:
        """
        Gather last letters of all versions of shifted versions of text
        :param shifted_texts: versions of original text shifted on one char
        :return: gathered text which consist of last letters of shifted texts
        """
        last_letters = []
        for item in shifted_texts:
            last_letters.append(item[-1])
        return ''.join(last_letters)

    @classmethod
    def encode(cls, text: str) -> (str, int):
        """
        Encode text with BWT algorithm
        :param text: original text
        :return: tuple encoded text and index of original in shifted_texts
        """
        shifted_texts = cls.shifted_texts(text)
        shifted_texts.sort()
        encoded_index = cls._calc_origin_index(shifted_texts, text)
        encoded_word = cls._last_letter_text(shifted_texts)
        return encoded_word, encoded_index

    @staticmethod
    def _get_index_and_remove_by_letter(
            encoded_letters: List[Tuple[str, int]],
            searched_letter: str,
    ) -> int:
        """
        Find first tuple in encoded_letters with first position
        equal searched_letter, remove it from encoded_letters and
        return second position of the tuple
        :param encoded_letters: (letter, index by alphabet)
        :param searched_letter: one letter or sign we are looking for
        :return: index by alphabet
        """
        for item in encoded_letters:
            if item[0] == searched_letter:
                searched_index = item[1]
                encoded_letters.remove(item)
                return searched_index

        return -1

    @staticmethod
    def _get_and_remove_by_index(
            signs_chain: List[Tuple[int, str, int]],
            searched_index: int,
    ) -> (str, int):
        """
        Find first tuple in signs_chain with first position
        equal searched_index, remove it from signs_chain and return second
        and third position of the tuple
        :param signs_chain: (index, letter, next item index)
        :param searched_index: index we are looking for (first position)
        :return: letter and next item index
        """
        for item in signs_chain:
            if item[0] == searched_index:
                signs_chain.remove(item)
                return item[1], item[2]
        return '', -1

    @classmethod
    def _get_signs_chain(cls, encoded_text: str) -> List[Tuple[int, str, int]]:
        """
        Generate signs_chain list of tuples like (index, sign, next item index)
        for OPTIMIZED decoding with BWT algorithm
        :param encoded_text: previously encoded text
        :return: list of tuples like (index, sign, next item index)
        """
        sorted_chars = [
            (letter, ind) for ind, letter in enumerate(sorted(encoded_text))
        ]
        encoded_letters = [
            (letter, cls._get_index_and_remove_by_letter(sorted_chars, letter))
            for letter in encoded_text
        ]
        signs_chain = [
            (prev_ind, letter, next_ind)
            for prev_ind, (letter, next_ind) in enumerate(encoded_letters)
        ]
        return signs_chain

    @classmethod
    def decode(cls, encoded_text: str, encoded_index: int) -> str:
        """
        Decode encoded text with BWT algorithm
        :param encoded_text: previously encoded text
        :param encoded_index: index of original in shifted texts
        :return: decoded original text
        """
        text_signs_reversed = []

        signs_chain = cls._get_signs_chain(encoded_text)

        curr_index = encoded_index
        while signs_chain:
            letter, curr_index = cls._get_and_remove_by_index(
                signs_chain, curr_index
            )
            text_signs_reversed.append(letter)

        original_text = text_signs_reversed[::-1]
        return ''.join(original_text)


if __name__ == '__main__':
    text_sample = 'Testing phrase for Burrows-Wheeler transformation.'

    bwt = BurrowsWheelerTransform()
    encoded_sample, index = bwt.encode(text_sample)
    decoded_sample = bwt.decode(encoded_sample, index)

    stat = SamplesStatistic(text_sample, encoded_sample, decoded_sample)
    stat.samples_statistic()
