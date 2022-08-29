var moment = require('moment');
var express = require('express');
var router = express.Router();
var db = require('../db/postgresql')
var utils = require('./utils')

function formatRecord(record) {
    delete record.record_id
    record.timestamp = utils.createDateAsUTC(record.timestamp)
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
        // Table not found
        if (error.code === "42P01") {
            error.status = 404
        }
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
        // Table not found
        if (error.code === "42P01") {
            error.status = 404
        }
        next(error)
    }
})

router.get('/:cryptoSymbol/:currencySymbol/:start_date/:end_date', async function (req,
                                                                 res,
                                                                 next) {
    try {
        const start_date = utils.createDateAsUTC(moment(req.params.start_date, "YYYYMMDDhhmmss").toDate())
        const end_date = utils.createDateAsUTC(moment(req.params.end_date, "YYYYMMDDhhmmss").toDate())
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
        // Table not found
        if (error.code === "42P01") {
            error.status = 404
        }
        next(error)
    }
})

module.exports = router;
