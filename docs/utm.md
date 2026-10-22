# UTM-метки (источник трафика)

Middleware `apps/rentals/middleware.py` сохраняет в сессии параметры `utm_source` (или алиас `src`) и `utm_campaign`. При оформлении заказа визардом значения записываются в `RentalOrder.traffic_source` и `RentalOrder.traffic_campaign` и сохраняются до оплаты.

## Конструктор в админке
Страница `/admin/utm-builder/` (кнопка «Конструктор UTM-ссылок» на панели владельца): выбираете целевую страницу, источник (с подсказками площадок), канал, кампанию и вариант креатива — сервис собирает полную ссылку, кнопка «Копировать» копирует её в буфер.

## Где смотреть
- Фильтры `traffic_source` и `traffic_campaign` в `/admin/rentals/rentalorder/`
- Карточка «Источники трафика» на дашборде владельца — таблица `Источник | Кампания | Заказов | Клиентов | Выручка` (пустые — `(без метки)` и `(без кампании)`)

## Примеры рекламных ссылок
| Источник | Ссылка |
|---|---|
| ВКонтакте | `https://selfstorage.kislyakov.pro/?utm_source=vk` |
| Google Ads | `https://selfstorage.kislyakov.pro/?utm_source=google` |
| Яндекс.Директ (на бокс) | `https://selfstorage.kislyakov.pro/orders/wizard/?box=1&utm_source=yandex` |
| Facebook | `https://selfstorage.kislyakov.pro/?utm_source=facebook&utm_campaign=vesna` |
| Instagram (алиас src) | `https://selfstorage.kislyakov.pro/?src=instagram` |
| VK с кампанией | `https://selfstorage.kislyakov.pro/?utm_source=vk&utm_campaign=vesna` |

После `seed_demo` есть тестовые заказы с метками `vk`, `google`, `direct`, `demo`, кампаниями `vesna` и `lyto`.
