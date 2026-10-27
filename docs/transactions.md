# Transactions

A transaction is a group of database operations that should work as one operation.

The main commands are:

- BEGIN - starts a transaction
- COMMIT - saves all changes
- ROLLBACK - cancels all changes in the transaction

## Payment and PaymentAttempt

When a payment is created, I also create a PaymentAttempt.

Both records should be created in one transaction.

The repository uses flush() after creating the Payment. This sends the INSERT to PostgreSQL and gives us the payment ID, but the transaction is still open.

After that PaymentAttempt can be created with this payment ID.

Only after both operations succeed do we call commit().

If something fails between these operations, rollback() removes all changes from the current transaction.

I tested this by deliberately raising an exception before PaymentAttempt was created. After rollback, neither Payment nor PaymentAttempt existed in the database.

## Concurrency and lost update

Two transactions can work with the same row at the same time.

In my test the payment amount starts at 100.

Two database sessions both read 100 and both add 10.

The first transaction saves 110.

The second transaction also saves 110 because it was working with the old value.

The final result is 110 instead of 120.

This is called a lost update.

## SELECT FOR UPDATE

SELECT FOR UPDATE can be used when we want to lock a row before changing it.

For example:

SELECT * FROM payments
WHERE id = 1
FOR UPDATE;

The first transaction locks the row.

If another transaction tries to lock the same row, it waits until the first transaction finishes with COMMIT or ROLLBACK.

This is pessimistic locking.

## Read Committed

PostgreSQL uses Read Committed as the default transaction isolation level.

A query sees data that was committed before that query started.

Because different queries can see newer committed data, concurrency problems are still possible if several transactions modify the same row without locking.

## Optimistic and pessimistic locking

Pessimistic locking locks the database row before changing it. SELECT FOR UPDATE is an example.

Optimistic locking usually does not lock the row immediately. Instead it can use a version number and check that the row was not changed by another transaction before saving.

Locks are useful when several requests can modify the same data and we need to avoid conflicts or lost updates.