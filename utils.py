import sys

import requests


class StringSample:
    """
    Class for generating some string data
    """
    @staticmethod
    def get_html_str_data_by_url(url_: str) -> str:
        """
        Return html data, from response from url_ site
        :param url_: url parameter, which we should request
        :return: text of the response from request
        """
        response = requests.get(url_)
        if response is not None:
            text = response.text
        else:
            text = ''
        return text


class SamplesStatistic:
    """
    Class for gathering and analyzing original, encoded and decoded samples
    for different information encoding algorithms
    """
    def __init__(self, original: str, encoded, decoded: str):
        self._original_text = original
        self._encoded_value = encoded
        self._decoded_text = decoded

    def equality_check(self) -> bool:
        """
        Check equality of original and decoded samples and print answer
        :return: True if samples are equal else False
        """
        if self._original_text == self._decoded_text:
            print('Original and decoded samples are equal')
            is_equal = True
        else:
            print('Original and decoded samples are different.')
            is_equal = False
        return is_equal

    def _memory_statistic(self) -> None:
        """
        Gather memory usage statistic of original and encoded samples
        :return: None
        """
        original_size = sys.getsizeof(self._original_text)
        encoded_size = sys.getsizeof(self._encoded_value)
        ratio = original_size / encoded_size
        print(f'Original size is {original_size} bits')
        print(f'Encoded size is {encoded_size} bits')
        print(
            f'Encoded sample takes up {ratio:.3f}',
            'times lesser memory than original'
        )

    def samples_statistic(self, memory=False, show_samples=True) -> None:
        """
        General function for gathering statistic data about information samples
        :param memory: flag, represents should we gather memory statistic
        :param show_samples: flag, represents should we print original,
        encoded and decoded samples
        :return: None
        """
        if self.equality_check():
            if show_samples:
                print(f'Original sample: {self._original_text}')
                print(f'Encoded sample: {self._encoded_value}')
                print(f'Decoded sample: {self._decoded_text}')
            if memory:
                self._memory_statistic()
        else:
            print('Something go wrong')