var express = require('express');
var router = express.Router();

SAMPLE_DATA = [
    {
        'timestamp': new Date(2022, 8, 6, 13, 0, 0),
        'open': 1335.2,
        'high': 1452.31,
        'low': 1234.21,
        'close': 1450.,
    },
    {
        'timestamp': new Date(2022, 8, 6, 14, 0, 0),
        'open': 1450.,
        'high': 1472.31,
        'low': 1234.21,
        'close': 1321.37,
    },
    {
        'timestamp': new Date(2022, 8, 6, 15, 0, 0),
        'open': 1321.37,
        'high': 1652.31,
        'low': 1134.21,
        'close': 1475.4,
    },
    {
        'timestamp': new Date(2022, 8, 6, 16, 0, 0),
        'open': 1475.4,
        'high': 1643.1,
        'low': 1341.2,
        'close': 1400.,
    },
    {
        'timestamp': new Date(2022, 8, 6, 17, 0, 0),
        'open': 1400.,
        'high': 1482.31,
        'low': 1231.21,
        'close': 1290.2,
    },
    {
        'timestamp': new Date(2022, 8, 6, 18, 0, 0),
        'open': 1290.2,
        'high': 1555.5,
        'low': 1097.1,
        'close': 1550.1,
    }
]

router.get('/:crytoSymbol/:currencySymbol/:n_records', function (req,
                                                                 res,
                                                                 next){

})
