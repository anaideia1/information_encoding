import math

from bitarray import bitarray


class BloomFilter:
    """
    Class for representing Bloom filter functionality.
    Class instance store a filter and number of hash functions.
    """
    # desired/allowed probability of error true
    PROBABILITY_FALSE_TRIGGER = 0.01

    def __init__(self, expected_num_elements: int) -> None:
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


if __name__ == '__main__':
    bloom_filter = BloomFilter(1000000)
