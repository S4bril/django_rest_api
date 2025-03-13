from rest_framework import serializers
from fu_api.models.loaction_model import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['latitude', 'longitude']

    def validate(self, data):
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if (-180.0 > longitude > 180.0):
            raise serializers.ValidationError("longitude has to be in range from -180 degrees to 180 degrees")

        if (-90.0 > latitude > 90.0):
            raise serializers.ValidationError("latitude has to be in range from -90.0 degrees to 90.0 degrees")
        return data