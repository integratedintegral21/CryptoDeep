const HOST = 'localhost'
const PORT = 5432
const DB = 'cryptodb'
const USER = 'cryptodb'
const PASSWORD = 'cryptodb'


const pgp = require('pg-promise')(/* options */)
const db = pgp('postgres://' + USER + ':' + PASSWORD + '@' + HOST + ':' + PORT + '/' + DB)

const convertToPostgresqlFormat = (date) => {
    return date.toISOString().replace('T', ' ').replace('Z', '')
}

async function get_all_records(crypto, currency) {
    const table_name = crypto + '_' + currency + '_records'
    return await db.many('SELECT * FROM ' + table_name)
}

async function get_n_latest_records(crypto, currency, n_records) {
    const table_name = crypto + '_' + currency + '_records'
    const sql = 'SELECT * FROM ' + table_name + ' ORDER BY timestamp DESC LIMIT '
        + n_records
    return await db.many(sql)
}

async function get_records_between(crypto, currency, start_date, end_date) {
    const table_name = crypto + '_' + currency + '_records'
    const sql = 'SELECT * FROM ' + table_name + ' WHERE timestamp BETWEEN $1 AND $2'
    return await db.many(sql, [convertToPostgresqlFormat(start_date), convertToPostgresqlFormat(end_date)])
}

module.exports.get_all_records = get_all_records
module.exports.get_n_latest_records = get_n_latest_records
module.exports.get_records_between = get_records_between
