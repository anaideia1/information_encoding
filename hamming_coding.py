from bitarray import bitarray
from typing import Iterator, List, Generator

from utils import SamplesStatistic


class HammingCoder:
    """
    Class for encoding and decoding texts via Hamming codes.
    Class instance store a number of characters in one chunk.
    """
    def __init__(self, single_message_length_in_char: int) -> None:
        self.num_of_char = single_message_length_in_char

    @staticmethod
    def _chunk_to_b_array(chunk_str: str) -> bitarray:
        """
        Transform string variable to bitarray variable via utf-8
        :param chunk_str: string variable, which we should transform.
        :return: created bitarray variable.
        """
        b_array = bitarray()
        for encoded_char in chunk_str.encode('utf-8'):
            b_array += bitarray('{:0>8}'.format(format(encoded_char, 'b')))
        return b_array

    def _from_str_to_b_arrays(self, origin_str: str) -> Iterator[bitarray]:
        """
        Split original text to chunk with self.num_of_char length and
        encode it with utf-8 and transform it to bitarray
        :param origin_str: text, which we are encoding
        :return: generator with encoded bitarrays
        """
        chunks_str = (
            origin_str[i:i + self.num_of_char]
            for i in range(0, len(origin_str), self.num_of_char)
        )
        b_arrays = (self._chunk_to_b_array(chunk) for chunk in chunks_str)
        return b_arrays

    @staticmethod
    def _split_chunk(chunk: bitarray) -> Iterator[bitarray]:
        """
        Generator-function which split our bitarray chunk to
        bitarray of smaller length (0, 1, 3, 7, ..., (2**n-1), etc)
        for inserting informational bits.
        :param chunk: bitarray of particular length (8 * self.num_of_char)
        :return: generator-object
        """
        i = 1
        first_ind = 0
        last_ind = 0
        yield bitarray()
        while last_ind <= len(chunk):
            last_ind = first_ind + 2**i - 1
            yield chunk[first_ind:last_ind]
            first_ind += 2**i-1
            i += 1

    @classmethod
    def _add_info_bits(cls, chunk: bitarray) -> bitarray:
        """
        Split bitarray chunk on smaller chunks via self._split_chunk
        and collect its back into one chunk with informational bits inserted
        :param chunk: bitarray of particular length (8 * self.num_of_char)
        :return: bitarray with informational bits inserted
        """
        collected_chunk = bitarray()

        parted_chunk = cls._split_chunk(chunk)
        for part in parted_chunk:
            collected_chunk += bitarray('0')
            collected_chunk += part

        return collected_chunk

    @staticmethod
    def _control_bit(it: bitarray, position: int) -> Iterator[int]:
        """
        Generator function for extracting and collecting bits  from whole chunk
        which are controlled by informational bit on position n
        :param it: chunk bitarray
        :param position: position of informational bit
        :return: generator-object
        """
        it = iter(it)
        try:
            for _ in range(position-1):
                next(it)
            while True:
                for _ in range(position):
                    yield next(it)
                for _ in range(position):
                    next(it)
        except StopIteration:
            return

    @classmethod
    def _set_info_bits(cls, chunk_bin: bitarray) -> None:
        """
        Set values of informational bits in our extended chunk with values
        which depends on controlled bit by this informational bit
        :param chunk_bin: extended with informational bit chunk bitarray
        :return: None
        """
        i = -1
        while 2**(i+1) < len(chunk_bin):
            i += 1

        while i >= 0:
            counter = list(cls._control_bit(chunk_bin, 2**i)).count(1)
            chunk_bin[2**i-1] = counter % 2
            i -= 1

    @classmethod
    def _encode_chunk(cls, chunk_bin: bitarray) -> bitarray:
        """
        Encode one particular chunk of origin text
        :param chunk_bin: particular chunk bitarray for self.num_of_character
        letter in original text encoded with utf-8
        :return: encoded by hamming algorithm chunk
        """
        encoded_chunk = cls._add_info_bits(chunk_bin)
        cls._set_info_bits(encoded_chunk)
        return encoded_chunk

    def encode(self, origin_str: str) -> List[bitarray]:
        """
        Transform original string text to bit with utf-8 and encode it
        by hamming algorithm
        :param origin_str: origin text, which we should encode
        :return: list with encoded by hamming algorith chunks
        """
        origin_chunks = self._from_str_to_b_arrays(origin_str)
        encoded_chunks = [self._encode_chunk(chunk) for chunk in origin_chunks]
        return encoded_chunks

    @staticmethod
    def _extract_value_bits(encoded_chunk: bitarray) -> bitarray:
        """
        Extract and collect value bits of encoded chunk
        :param encoded_chunk: encoded bitarray chunk
        :return: bitarray only with value bits
        """
        value_bits = bitarray()
        start, i = 2, 1
        while start < len(encoded_chunk):
            end = start + 2**i - 1
            value_bits += encoded_chunk[start:end]
            start = end + 1
            i += 1
        return value_bits

    @staticmethod
    def _extract_info_bits(encoded_chunk: bitarray) -> bitarray:
        """
        Extract and collect informational bits of encoded chunk
        :param encoded_chunk: encoded bitarray chunk
        :return: bitarray only with informational bits
        """
        info_bits = bitarray()
        i = 0
        while 2**i < len(encoded_chunk):
            info_bits += encoded_chunk[2**i-1:2**i]
            i += 1
        return info_bits

    @staticmethod
    def _reverse_by_index(received: bitarray, err_ind: int) -> bitarray:
        """
        Reverse bit in bitarray on position err_ind
        :param received: bitarray with error in one bit
        :param err_ind: position of bit with error
        :return: received bitarray with reversed bit on err_ind position
        """
        received[err_ind] = (received[err_ind] + 1) % 2
        return received

    @classmethod
    def _restore_chunk(
            cls,
            received: bitarray,
            newly_encoded: bitarray,
    ) -> bitarray:
        """
        Find and fix one bit in bitarray with error
        :param received: received bitarray with error bit
        :param newly_encoded: bitarray encoded on value bits we receive
        :return: received bitarray with fixed bit
        """
        received_info_bits = cls._extract_info_bits(received)
        new_info_bits = cls._extract_info_bits(newly_encoded)

        diff_indexes = [2**i for i in range(len(received_info_bits))
                        if received_info_bits[i] != new_info_bits[i]]

        error_index = sum(diff_indexes) - 1
        restored_received = cls._reverse_by_index(received, error_index)

        return restored_received

    @classmethod
    def _validate_chunks(
            cls,
            received_chunks: List[bitarray],
            new_encoded_chunks: Iterator[bitarray],
    ) -> List[bitarray]:
        """
        Compare all received bitarray with newly encoded on only
        value bits we received and correct one bit in case of difference
        :param received_chunks: list of received chunks
        :param new_encoded_chunks: list of encoded on value bits we received
        :return: list of compared and fixed chunks
        """
        checked_chunks = []
        for received, new_encoded in zip(received_chunks, new_encoded_chunks):
            if received == new_encoded:
                res = received
            else:
                res = cls._restore_chunk(received, new_encoded)
            checked_chunks.append(res)
        return checked_chunks

    def _from_bits_to_str(self, chunks: Iterator[bitarray]) -> str:
        """
        Translate received and extracted value bits from bitarray chunks to
        one decoded string
        :param chunks:
        :return:
        """
        res_str = ''
        for chunk in chunks:
            for i in range(self.num_of_char):
                char_bin = chunk[8*i:8*(i+1)]
                if char_bin:
                    res_str += chr(int(char_bin.to01(), base=2))
        return res_str

    def decode(self, encoded_chunks):
        """
        Receive encoded chunk, test it on accuracy with hamming algorithm,
        fix if it needed and decode it to string format
        :param encoded_chunks: list of encoded by hamming algorithm bitarrays
        :return: decoded text
        """
        extracted_chunks = map(self._extract_value_bits, encoded_chunks)
        newly_encoded_chunks = map(self._encode_chunk, extracted_chunks)

        restored_chunks = self._validate_chunks(
            encoded_chunks, newly_encoded_chunks
        )

        res_chunks = map(self._extract_value_bits, restored_chunks)
        res_str = self._from_bits_to_str(res_chunks)
        return res_str


if __name__ == '__main__':
    origin_sample = 'Hamming coding.'

    hamming_coder = HammingCoder(3)
    encoded_sample = hamming_coder.encode(origin_sample)
    decoded_sample = hamming_coder.decode(encoded_sample)

    stat = SamplesStatistic(origin_sample, encoded_sample, decoded_sample)
    stat.samples_statistic()
