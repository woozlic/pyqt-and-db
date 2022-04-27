import logging
import os


format = logging.Formatter('%(asctime)-10s %(levelname)s %(module)s %(message)s')
current_directory = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_directory, 'files')
log_filename = os.path.join(log_path, 'client.log')

handler = logging.FileHandler(filename=log_filename, encoding='utf-8')
handler.setLevel(logging.DEBUG)
handler.setFormatter(format)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(format)
server_logger = logging.getLogger('client')
server_logger.addHandler(handler)
server_logger.addHandler(stream_handler)
server_logger.setLevel(logging.INFO)

if __name__ == '__main__':
    logger = logging.getLogger('client')
    logger.debug('Testing')
    logger.info('Testing')
    logger.error('Testing')
