var moment = require('moment');
var express = require('express');
var router = express.Router();
var db = require('../db/postgresql');
const utils = require("./utils");

function formatPrediction(pred) {
    delete pred.prediction_id
    pred.timestamp = utils.createDateAsUTC(pred.timestamp)
    return pred
}

router.get('/:cryptoSymbol/:currencySymbol/all', async function (req,
                                                                      res,
                                                                      next) {
    try {
        const predictions = (await db.get_all_predictions(req.params.cryptoSymbol, req.params.currencySymbol))
        predictions.map(formatPrediction)
        res.send(
            predictions.sort((a, b) => {
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

router.get('/:cryptoSymbol/:currencySymbol/:n_records', async function(req,
                                                                       res,
                                                                       next) {
    try {
        const records = (await
            db.get_n_latest_predictions(req.params.cryptoSymbol, req.params.currencySymbol, req.params.n_records))
        records.map(formatPrediction)
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
            db.get_predictions_between(req.params.cryptoSymbol, req.params.currencySymbol, start_date, end_date))
        records.map(formatPrediction)
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