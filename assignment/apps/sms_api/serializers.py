from rest_framework import serializers


class SMSData(object):
    def __init__(self, sms_from, sms_to, sms_text):
        self.sms_from = sms_from
        self.sms_to = sms_to
        self.sms_text = sms_text


class SMSDataSerializer(serializers.Serializer):
    sms_from = serializers.CharField(required=True, min_length=6, max_length=16)
    sms_to = serializers.CharField(required=True, min_length=6, max_length=16)
    sms_text = serializers.CharField(required=True, min_length=1, max_length=120)


    def create(self, validated_data):
        return SMSData(**validated_data)
