from django.db import connection

from rest_framework import generics, serializers
from rest_framework.response import Response

from .serializers import AddReadingSerializer


class AddReadingsView(generics.CreateAPIView):
    serializer_class = AddReadingSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


def _raw_sql(query, params):
    with connection.cursor() as cursor:
        cursor.execute(query, params=params)
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


class ListReadingsByMixin():

    class RequestParamsSerializer(serializers.Serializer):
        """
        Used for processing the GET parameters
        """
        from_date = serializers.DateTimeField(required=False)
        to_date = serializers.DateTimeField(required=False)
        aggregation_size_minutes = serializers.IntegerField(required=False, min_value=1, default=5)

    @classmethod
    def parse_request_params(cls, request):
        s = cls.RequestParamsSerializer(data=request.GET)
        if not s.is_valid():
            raise serializers.ValidationError(s.errors)
        return s.validated_data

    @staticmethod
    def build_filters(request_params, query_params):
        filters = ''

        if 'from_date' in request_params:
            filters += ' and r.timestamp >= %(from_date)s'
            query_params['from_date'] = request_params['from_date']

        if 'to_date' in request_params:
            filters += ' and r.timestamp <= %(to_date)s'
            query_params['to_date'] = request_params['to_date']

        return filters

    @staticmethod
    def fill_in_params(data, request_params):
        for d in data:
            d['aggregation_size_minutes'] = request_params['aggregation_size_minutes']
            d['from_date'] = request_params.get('from_date')
            d['to_date'] = request_params.get('to_date')


class ListReadingsByDeviceView(generics.ListAPIView, ListReadingsByMixin):

    def list(self, request, device_id):
        request_params = self.parse_request_params(request)

        query_params = dict(device_id=device_id, seconds=request_params['aggregation_size_minutes'] * 60)

        query = """
            select
                d.customer_id,
                d.id as device_id,
                (
                    select
                        array_agg(row_to_json(a))
                    from
                        (
                            select
                                avg(r.reading) as "value",
                                to_timestamp(floor(extract('epoch' from r.timestamp) / %(seconds)s) * %(seconds)s) as "from"
                            from
                                myapp_reading as r
                            where
                                r.device_id = d.id {filters}
                            group by
                                "from"
                            order by
                                "from"
                        ) as a
                ) as aggregated_values
            from
                myapp_device as d
            where
                d.id = %(device_id)s
        """

        filters = self.build_filters(request_params, query_params)

        data = _raw_sql(query.format(filters=filters), params=query_params)

        self.fill_in_params(data, request_params)

        return Response({'data': data})


class ListReadingsByCustomerView(generics.ListAPIView, ListReadingsByMixin):

    def list(self, request, customer_id):
        request_params = self.parse_request_params(request)

        query_params = dict(customer_id=customer_id, seconds=request_params['aggregation_size_minutes'] * 60)

        query = """
            select
                d.customer_id,
                d.id as device_id,
                (
                    select
                        array_agg(row_to_json(a))
                    from
                        (
                            select
                                avg(r.reading) as "value",
                                to_timestamp(floor(extract('epoch' from r.timestamp) / %(seconds)s) * %(seconds)s) as "from"
                            from
                                myapp_reading as r
                            where
                                r.device_id = d.id {filters}
                            group by
                                "from"
                            order by
                                "from"
                        ) as a
                ) as aggregated_values
            from
                myapp_device as d
            where
                d.customer_id = %(customer_id)s
        """

        filters = self.build_filters(request_params, query_params)

        data = _raw_sql(query.format(filters=filters), params=query_params)

        self.fill_in_params(data, request_params)

        return Response({'data': data})
