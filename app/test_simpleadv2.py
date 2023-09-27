# pip3 install -U pytest
# pytest

from simpleadv2 import SimpleAdv2Writer

def test_add_user_metadata_tag():
    adv_writer = SimpleAdv2Writer()
    adv_writer.add_user_metadata_tag('TAG1', 'VALUE1')
    adv_writer.add_user_metadata_tag('TAG2', 'VALUE2')
    adv_writer.add_user_metadata_tag('TAG3', 'VALUE3')
    adv_writer.add_user_metadata_tag('TAG2', 'VALUE4')

    assert adv_writer._user_metadata_tags == [('TAG1', 'VALUE1'), ('TAG2', 'VALUE4'), ('TAG3', 'VALUE3')]
