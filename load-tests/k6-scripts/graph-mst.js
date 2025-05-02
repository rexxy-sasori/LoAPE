import http from 'k6/http';
import { check } from 'k6';

export default function () {
    const url = 'http://quarkus-graph-mst.default.172.16.13.92.sslip.io/graph-mst';
    const payload = JSON.stringify({
        size: 'small',
    });

    const headers = {
        'Content-Type': 'application/json',
    };

    const response = http.post(url, payload, { headers: headers });

    // Check if the request was successful
    check(response, {
        'status is 200': (r) => r.status === 200,
    });
}
