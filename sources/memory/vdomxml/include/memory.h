
#define release_one_on_stockpile(stockpile) release_on_stockpile(stockpile, 1)


static int
initialize_stockpile(Stockpile *stockpile, unsigned int item_size, unsigned int items_per_batch)
{
    Batch *batch;

    stockpile->item_size = item_size;
    stockpile->items_per_batch = items_per_batch;
    stockpile->batch_size = item_size * items_per_batch;

    batch = (Batch *)malloc(sizeof(Batch) + stockpile->batch_size);
    if (!batch)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unable to allocate memory");
        return 1;
    }

    batch->prev = NULL;
    batch->next = NULL;
    batch->counter = 0;

    stockpile->list = batch;
    stockpile->last = batch;
    stockpile->counter = 0;

    return 0;
}

static void
deinitialize_stockpile(Stockpile *stockpile)
{
    Batch *batch, *next;
    for (batch = stockpile->list; batch; batch = next)
    {
        next = batch->next;
        free(batch);
    }
}

static void *
allocate_on_stockpile(Stockpile *stockpile)
{
    void *item;

    if (stockpile->last->counter == stockpile->items_per_batch)
    {
        if (stockpile->last->next)
        {
            stockpile->last = stockpile->last->next;
            stockpile->last->counter = 0;
        }
        {
            Batch *batch;
            batch = malloc(sizeof(Batch) + stockpile->batch_size);
            if (!batch)
            {
                PyErr_SetString(PyExc_RuntimeError, "Unable to allocate memory");
                return NULL;
            }

            batch->prev = stockpile->last;
            batch->next = NULL;
            batch->counter = 0;

            stockpile->last->next = batch;
            stockpile->last = batch;
        }
    }

    item = (void *)((char *)(stockpile->last) + sizeof(Batch) + (stockpile->last->counter) * stockpile->item_size);

    stockpile->last->counter++;
    stockpile->counter++;

    return item;
}

static void
release_on_stockpile(Stockpile *stockpile, unsigned int counter)
{
    while (counter)
    {
        if (counter > stockpile->last->counter)
        {
            counter -= stockpile->last->counter;
            stockpile->last = stockpile->last->prev;
        }
        else
        {
            stockpile->last->counter -= counter;
            counter = 0;
        }
    }
}

static void
release_all_on_stockpile(Stockpile *stockpile)
{
    stockpile->last = stockpile->list;
    stockpile->counter = stockpile->last->counter = 0;
}

static int
iterate_stockpile(Stockpile *stockpile, StockpileIterateCallback function)
{
    Batch *batch = stockpile->list;
    while (batch)
    {
        char *item = (char *)batch + sizeof(Batch);
        char *stop = item + batch->counter * stockpile->item_size;

        while (item < stop)
        {
            if (function(item))
                return 1;
            item += stockpile->item_size;
        }

        if (batch == stockpile->last)
            break;
        else
            batch = batch->next;
    }
    return 0;
}
