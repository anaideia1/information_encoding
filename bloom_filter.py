import math

from bitarray import bitarray
from utils import StringSample


class BloomFilter:
    """
    Class for representing Bloom filter functionality.
    Class instance store a filter and number of hash functions.
    """
    # desired/allowed probability of error true
    PROBABILITY_FALSE_TRIGGER = 0.01

    def __init__(self, expected_num_elements: int) -> None:
        self._expected_num_elements = expected_num_elements
        self._filter_len = self._calc_filter_length(expected_num_elements)

        self._filter = bitarray(self._filter_len)
        self._filter.setall(0)

        self._num_hash_func = self._calc_num_hash_func(expected_num_elements)

    def _calc_filter_length(self, expected_num_elements: int) -> int:
        """
        Calculate optimal filter length depending on expected number of elems
        :param expected_num_elements: expected number of elements
        :return: optimal length of filter
        """
        filter_length = math.floor(
            -expected_num_elements
            * math.log(self.PROBABILITY_FALSE_TRIGGER)
            / (math.log(2) * math.log(2))
        )
        return filter_length

    def _calc_num_hash_func(self, expected_num_elements: int) -> int:
        """
        Calculate optimal number of hash functions depending on filter length
        and expected number of elements
        :param expected_num_elements: expected number of elements
        :return: optimal number of hash functions
        """
        number_hash_func = round(
            (self._filter_len / expected_num_elements) * math.log(2)
        )
        return number_hash_func

    def _parameterized_hash_func(self, new_item: str, parameter: int) -> int:
        """
        Parameterized hash function for string value
        :param new_item: string value which we want to hash
        :param parameter: parameter for functions
        :return: parameterized hash
        """
        parameterized_value = str(parameter) + new_item

        hash_value = 5381
        for letter in parameterized_value:
            hash_value = ((hash_value << 5) + hash_value) + ord(letter)

        return hash_value % self._filter_len

    def check_is_not_in_filter(self, item: str) -> bool:
        """
        Check if item was added to filter
        :param item: item which we should check
        :return: True if item was added to filter, else False
        """
        for i in range(self._num_hash_func):
            if self._filter[self._parameterized_hash_func(item, i)] == 0:
                return True
        return False

    def add_to_filter(self, new_item: str) -> None:
        """
        Add item to filter
        :param new_item: item which we should add to filter
        :return: None
        """
        for i in range(self._num_hash_func):
            self._filter[self._parameterized_hash_func(new_item, i)] = 1

    def filter_test(self, test_string: str) -> None:
        """
        Testing filter with adding every fifth word of test_string.
        :param test_string: text for testing
        :return: None
        """
        test_parts = list(set(test_string.split(' ')))
        false_true_counter = 0
        true_counter = 0

        # adding in filter elements, what we can divide at 5
        for i, part in enumerate(test_parts):
            if i % 5 == 0:
                self.add_to_filter(part)

        # checking
        for i, part in enumerate(test_parts):
            if i % 5 != 0 and not self.check_is_not_in_filter(part):
                false_true_counter += 1
            if not self.check_is_not_in_filter(part):
                true_counter += 1

        print('Length of text testing sample ', len(test_parts))
        print('False true counter:', false_true_counter)
        print('General true counter:', true_counter)


if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/Bloom_filter'
    test_sample = StringSample.get_html_str_data_by_url(url)

    bloom_filter = BloomFilter(10000)

    bloom_filter.filter_test(test_sample)
