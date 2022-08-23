var express = require('express');
var router = express.Router();
var db = require('../db/postgresql')

router.get('/:cryptoSymbol/:currencySymbol/:n_records', async function (req,
                                                                 res,
                                                                 next){
    try {
        const records = await db.get_all_records(req.params.cryptoSymbol, req.params.currencySymbol)
        res.send(records.sort((a, b) => {
            if (a.timestamp < b.timestamp) {
                return -1
            }
            return 1
        }))
    } catch (error) {
        next(error)
    }
})

module.exports = router;
