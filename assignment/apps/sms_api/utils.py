from utils.caches import RedisStore


class StopRequestStore(RedisStore):

    ttl = 4*60*60
    check_exists = True
    
    @staticmethod
    def generate_key(keyParams):
        return 'stoprequest_%s' % ''.join(keyParams)

class OutboundSMSCounter(RedisStore):

    ttl = 24*60*60

    @staticmethod
    def generate_key(keyParams):
        return 'outboundsmscounter_%s' % keyParams[0]
