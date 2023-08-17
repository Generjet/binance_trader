# README

Дараах зүйлсийг имплемент хийх:

* Channel level үүсгэх бөгөөд хэрэв үнэ level-ээс хэтрээд явбал тухайн level-ийг дууссанд тооцож status=ended болгоно. Энэ үед stop_loss_trade table эхлүүлэх бөгөөд next channel үүсэх процессыг хүлээж ажиглан, тухайн шинэ суваг дотороо хамгийн өндөр цэг буюу таазанд хүрсэн үед нь зарна. Ингэснээр алдагдалтай яваа арилжааг буцаж дээшээ өгсөн ашигаа хийхийг хэт удаан хүлээлгүйгээр хамгийн алдагдал багатайгаар зарж дараачийн савалгаанд ашиг хийнэ.

 Харин level дотороо байвал status=started байх бөгөөд энэ үед buy=>sell хослол хийнэ.

Buy is allowed if:
status = started  # шинэ суваг нээгдсэн бөгөөд суваг дотор байгаа гэсэн үг учраас тэр

Sell is allowed if:
status = started 

Харин Stop_Loss trade-ийн хувьд:
if price < support+20 & orders.sell_date = nil # which means crypto is bought at some point(near support), but not sold yet because price dropped further below support.
then
create stop_loss_trade row:
1.   


* Micro time period scalping
5min period => set support and resistance.( can be set manually and automatically by python)
bounce trade within this channel

* orders belongs_to channel level . 
orders belongs_to signals . Because it has buy and sell, thus 2 signals must have
channel_level:
1. id
2. support
3. resistance

orders:
1. signals_id
2. channel_id

