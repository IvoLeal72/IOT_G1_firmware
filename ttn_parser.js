const toBinString = (bytes) =>
    bytes.reduce((str, byte) => str + byte.toString(2).padStart(8, '0'), '');

subPayload_sizes = [6, 3, 16, 18];

function sw_alarms_handler(data, subPayload_data) {
    if (!(data.hasOwnProperty('sw_alarms'))) {
        data.sw_alarms = [];
    }
    data.sw_alarms.push(parseInt(subPayload_data, 2));

    return true;
}

function hw_alarms_handler(data, subPayload_data) {
    if (!(data.hasOwnProperty('hw_alarms'))) {
        data.hw_alarms = [];
    }
    data.hw_alarms.push(parseInt(subPayload_data, 2));

    return true;
}

function open_request_handler(data, subPayload_data) {
    if (data.hasOwnProperty('open_request')) return false;
    data.open_request = parseInt(subPayload_data, 2);
    return true;
}

function open_reg_handler(data, subPayload_data) {
    if (!(data.hasOwnProperty('open_reg'))) {
        data.open_reg = [];
    }
    var open=subPayload_data.charAt(0)=='1'?true:false;
    var now=new Date();
    var startOfDay=Math.floor(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDay())/1000);
    var event_time=startOfDay+parseInt(subPayload_data.substr(1), 2);
    data.open_reg.push({
        open:open,
        event_epoch:event_time
    });
    return true;
}



subPayload_handlers = [sw_alarms_handler, hw_alarms_handler, open_request_handler, open_reg_handler];

function decodeUplink(input) {
    const view = new Uint8Array(input.bytes);
    bitString = toBinString(view);

    data = {};

    data.hw_version = parseInt(bitString.substr(0, 2), 2);
    data.api_version = parseInt(bitString.substr(2, 2), 2);
    data.batt = (parseInt(bitString.substr(4, 7), 2) * 2 + 250) * 10;

    var idx = 11;
    var error = false;
    while (true) {
        var type = bitString.substr(idx, 3);
        if (type.length != 3) {
            error = true;
            break;
        }
        idx += 3;
        var type_int = parseInt(type, 2);
        if (type_int == 7) break;
        if (type_int > 3) {
            error = true;
            break;
        }
        var to_get = subPayload_sizes[type_int];
        var subPayload_data = bitString.substr(idx, to_get);
        if (subPayload_data.length != to_get) {
            error = true;
            break;
        }
        idx += to_get;
        if(!subPayload_handlers[type_int](data, subPayload_data)){
            error=true;
            break;
        }
    }
    if (!error) data.size = idx;
    else data.error = true;


    return {
        data: data,
        warnings: [],
        errors: []
    };
}