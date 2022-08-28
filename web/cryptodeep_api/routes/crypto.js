var moment = require('moment');
var express = require('express');
var router = express.Router();
var db = require('../db/postgresql')

function createDateAsUTC(date) {
    return new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(),
        date.getSeconds()));
}

function formatRecord(record) {
    delete record.record_id
    record.timestamp = createDateAsUTC(record.timestamp)
    return record
}

router.get('/:cryptoSymbol/:currencySymbol/all', async function (req,
                                                                 res,
                                                                 next){
    try {
        const records = (await db.get_all_records(req.params.cryptoSymbol, req.params.currencySymbol))
        records.map(formatRecord)
        res.send(
            records.sort((a, b) => {
                if (a.timestamp < b.timestamp) {
                    return 1
                }
                return -1
            })
        )
    } catch (error) {
        next(error)
    }
})

router.get('/:cryptoSymbol/:currencySymbol/:n_records', async function (req,
                                                                 res,
                                                                 next){
    try {
        const records = (await
            db.get_n_latest_records(req.params.cryptoSymbol, req.params.currencySymbol, req.params.n_records))
        records.map(formatRecord)
        res.send(
            records.sort((a, b) => {
                if (a.timestamp < b.timestamp) {
                    return 1
                }
                return -1
            })
        )
    } catch (error) {
        next(error)
    }
})

router.get('/:cryptoSymbol/:currencySymbol/:start_date/:end_date', async function (req,
                                                                 res,
                                                                 next) {
    try {
        const start_date = createDateAsUTC(moment(req.params.start_date, "YYYYMMDDhhmmss").toDate())
        const end_date = createDateAsUTC(moment(req.params.end_date, "YYYYMMDDhhmmss").toDate())
        const records = (await
            db.get_records_between(req.params.cryptoSymbol, req.params.currencySymbol, start_date, end_date))
        records.map(formatRecord)
        res.send(
            records.sort((a, b) => {
                if (a.timestamp < b.timestamp) {
                    return 1
                }
                return -1
            })
        )
    } catch (error) {
        next(error)
    }
})

router.get('/pred/:cryptoSymbol/:currencySymbol/all', async function (req,
                                                                      res,
                                                                      next) {
    try {
        const predictions = (await db.get_all_predictions(req.params.cryptoSymbol, req.params.currencySymbol))
        predictions.map(formatRecord)
        res.send(
            predictions.sort((a, b) => {
                if (a.timestamp < b.timestamp) {
                    return 1
                }
                return -1
            })
        )
    } catch (error) {
        next(error)
    }
})

module.exports = router;
