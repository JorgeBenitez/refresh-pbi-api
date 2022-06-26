import logging
import time
import logging

def retry(delay, retries):
    def decorator(func):
        def wrapper(*args, **kargs):
            for i in range(retries):
                value = func(*args, **kargs)
                if value is not None and value is not False:
                    return value
                elif i == retries - 1:
                    logging.error(f'Max number of retries reached ({retries}) .')
                else:
                    logging.info(f'Process not finish. Waiting {delay} seconds to retry.')
                    time.sleep(delay)

            return None

        return wrapper
    return decorator


if __name__ == '__main__':

    logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(levelname)s:%(message)s')

    @retry(2, 3)
    def prueba():
        return False

    print(prueba())