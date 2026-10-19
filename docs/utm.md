# UTM-метки (источник трафика)

Middleware `apps/rentals/middleware.py` сохраняет в сессии параметр `utm_source` (или алиас `src`). При оформлении заказа визардом значение записывается в `RentalOrder.traffic_source` и сохраняется до оплаты.

## Где смотреть
- Фильтр `traffic_source` в `/admin/rentals/rentalorder/`
- Карточка «Источники трафика» на дашборде владельца — таблица `Источник | Заказов | Клиентов | Выручка` (пустые — `(без метки)`)

## Примеры рекламных ссылок
| Источник | Ссылка |
|---|---|
| ВКонтакте | `https://selfstorage.kislyakov.pro/?utm_source=vk` |
| Google Ads | `https://selfstorage.kislyakov.pro/?utm_source=google` |
| Яндекс.Директ (на бокс) | `https://selfstorage.kislyakov.pro/rentals/wizard/?box=1&utm_source=yandex` |
| Facebook | `https://selfstorage.kislyakov.pro/?utm_source=facebook&utm_campaign=vesna` |
| Instagram (алиас src) | `https://selfstorage.kislyakov.pro/?src=instagram` |

После `seed_demo` есть тестовые заказы с метками `vk`, `google`, `direct`, `demo`.
