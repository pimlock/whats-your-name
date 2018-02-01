import logging

logger = logging.getLogger(__name__)


class AppLinkSender(object):
    def __init__(self, sns, app_url):
        self.sns = sns
        self.app_url = app_url

    def send_link_to_phone_number(self, phone_number):
        message_text = 'You requested a link to the What\'sYourName app: {}'.format(self.app_url)

        # TODO figure out exact format of this
        message_attributes = {
            'maxPrice': {
                'DataType': 'Number',
                'StringValue': '0.2'
            }
        }
        response = self.sns.publish(
            PhoneNumber=phone_number,
            Message=message_text,
            MessageAttributes=message_attributes
        )
        logger.info('Published link to a phone number [%s], messageId: [%s]', phone_number, response.get('MessageId'))
