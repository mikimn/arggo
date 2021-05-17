from arggo import arggo


class TestMainAnnotation:
    def test_function_no_arguments(self):
        @arggo()
        def decorated():
            return 1

        assert decorated() == 1
