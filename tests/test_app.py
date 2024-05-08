from unittest.mock import patch, call

import sad.app

layer_sha = 'fa8ccbaed858cba63b1da6a1a9bf26cec588adb40627e78c6de81bbc3632d638'
test_event = {
    'ResourceProperties': {
        'BucketName': 'MyTestBucketName',
        'StaticAssetsLayerArn': 'MyTestLayerArn'
    }
}


@patch('sad.app.s3')
def test_upload(mock_s3):
    sad.app.dir = './tests/testfiles'
    result = sad.app.upload(test_event)
    assert result == layer_sha
    assert mock_s3.upload_file.call_args_list == [
        call(
            './tests/testfiles/file1.html',
            'MyTestBucketName',
            f'{layer_sha}/file1.html',
            ExtraArgs={
                'ContentType': 'text/html',
                'CacheControl': 'max-age=31536000, immutable'
            }
        ),
        call(
            './tests/testfiles/subdir/file2.js',
            'MyTestBucketName',
            f'{layer_sha}/subdir/file2.js',
            ExtraArgs={
                'ContentType': 'application/javascript',
                'CacheControl': 'max-age=31536000, immutable'
            }
        )
    ]


@patch('sad.app.s3')
def test_delete(mock_s3):
    sad.app.dir = './tests/testfiles'
    sad.app.delete_files(test_event)
    assert mock_s3.delete_object.call_args_list == [
        call(
            Bucket='MyTestBucketName',
            Key=f'{layer_sha}/file1.html'
        ),
        call(
            Bucket='MyTestBucketName',
            Key=f'{layer_sha}/subdir/file2.js'
        )
    ]
