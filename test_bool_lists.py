import datetime
import unittest
from decimal import Decimal
from fractions import Fraction

import dicttoxml


class ListBooleanValuesTest(unittest.TestCase):
    def test_list_tuple_generator_and_nested_values_are_lowercase(self):
        values = [True, False]
        generated = iter(values)

        self.assertIn(
            '<item type="bool">true</item><item type="bool">false</item>',
            dicttoxml.dicttoxml(values, return_bytes=False),
        )
        self.assertIn(
            '<item type="bool">true</item><item type="bool">false</item>',
            dicttoxml.dicttoxml(tuple(values), return_bytes=False),
        )
        generated_xml = dicttoxml.dicttoxml(generated, return_bytes=False)
        self.assertIn('<item type="bool">true</item>', generated_xml)
        self.assertIn('<item type="bool">false</item>', generated_xml)
        self.assertEqual([], list(generated))

        nested_xml = dicttoxml.dicttoxml(
            [[True], {'enabled': False}, [True, False]], return_bytes=False
        )
        self.assertIn('<item type="bool">true</item>', nested_xml)
        self.assertIn('<enabled type="bool">false</enabled>', nested_xml)
        self.assertEqual(2, nested_xml.count('<item type="bool">true</item>'))

    def test_list_inside_dict_and_attr_type_false(self):
        xml = dicttoxml.dicttoxml(
            {'flags': [True, False]}, attr_type=False, return_bytes=False
        )
        self.assertEqual(
            '<?xml version="1.0" encoding="UTF-8" ?>'
            '<root><flags><item>true</item><item>false</item></flags></root>',
            xml,
        )

    def test_cdata_matches_scalar_boolean_behavior(self):
        scalar = dicttoxml.dicttoxml(True, cdata=True, return_bytes=False)
        listed = dicttoxml.dicttoxml([True], cdata=True, return_bytes=False)

        self.assertIn('<root><item type="bool">true</item></root>', scalar)
        self.assertIn('<root><item type="bool">true</item></root>', listed)
        self.assertNotIn('<![CDATA[', scalar)
        self.assertNotIn('<![CDATA[', listed)

    def test_public_output_controls_remain_supported(self):
        item_func = lambda parent: 'entry'
        xml = dicttoxml.dicttoxml(
            [True, False],
            root=False,
            custom_root='flags',
            xml_declaration=False,
            ids=True,
            item_func=item_func,
            return_bytes=False,
        )
        self.assertTrue(xml.startswith('<entry '))
        self.assertNotIn('<root>', xml)
        self.assertNotIn('<?xml', xml)
        self.assertRegex(xml, r'<entry id="[^"]+" type="bool">true</entry>')
        self.assertRegex(xml, r'<entry id="[^"]+" type="bool">false</entry>')

        byte_xml = dicttoxml.dicttoxml([True], custom_root='flags')
        self.assertIsInstance(byte_xml, bytes)
        self.assertIn(b'<item type="bool">true</item>', byte_xml)

    def test_non_boolean_values_keep_existing_types_and_values(self):
        xml = dicttoxml.dicttoxml(
            [1, 1.5, 'café', None, Decimal('1.25'), Fraction(1, 3),
             datetime.datetime(2020, 1, 2, 3, 4, 5)],
            return_bytes=False,
        )
        self.assertIn('<item type="int">1</item>', xml)
        self.assertIn('<item type="float">1.5</item>', xml)
        self.assertIn('<item type="str">café</item>', xml)
        self.assertIn('<item type="null"></item>', xml)
        self.assertIn('<item type="number">1.25</item>', xml)
        self.assertIn('<item type="number">1/3</item>', xml)
        self.assertIn('<item type="str">2020-01-02T03:04:05</item>', xml)


if __name__ == '__main__':
    unittest.main()
