var moment = require('moment');
var express = require('express');
var router = express.Router();
var db = require('../db/postgresql')

function createDateAsUTC(date) {
    return new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(),
        date.getSeconds()));
}

router.get('/:cryptoSymbol/:currencySymbol/all', async function (req,
                                                                 res,
                                                                 next){
    try {
        const records = (await db.get_all_records(req.params.cryptoSymbol, req.params.currencySymbol))
        records.map((element) => {
            delete element.record_id
            element.timestamp = createDateAsUTC(element.timestamp).toISOString()
            return element
        })
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
        records.map((element) => {
            delete element.record_id
            element.timestamp = createDateAsUTC(element.timestamp).toISOString()
            return element
        })
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
                                                                 next){
    try {
        const start_date = createDateAsUTC(moment(req.params.start_date, "YYYYMMDDhhmmss").toDate())
        const end_date = createDateAsUTC(moment(req.params.end_date, "YYYYMMDDhhmmss").toDate())
        const records = (await
            db.get_records_between(req.params.cryptoSymbol, req.params.currencySymbol, start_date, end_date))
        records.map((element) => {
            delete element.record_id
            element.timestamp = createDateAsUTC(element.timestamp).toISOString()
            return element
        })
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

module.exports = router;
