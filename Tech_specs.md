ИНСТРУКЦИЯ К СЕБЕ

MASTER DEVELOPER MEGAPROMPT \& PRODUCT/TECHNICAL SPECIFICATION

Telegram Product • Architecture V1.3 • Developer Handoff • 19 August 2026

Единый мастер-промпт и техническое задание для разработчика/AI-coding-agent, который должен построить production-ready Telegram-продукт «Инструкция к себе».

0\. Роль разработчика

Ты — senior product engineer / solution architect. Твоя задача — реализовать систему, а не переизобретать психологическую модель.

Критический принцип:

\*\*Backend решает, ЧТО система имеет право утверждать. LLM решает только, КАК это объяснить человеку.\*\*

Нельзя:

менять утверждённые вопросы без новой версии question bank;

переносить scoring в LLM;

позволять LLM придумывать диагнозы, детство, травму или неподтверждённую причинность;

смешивать state и trait;

называть internal normalized score population percentile;

выдавать FULL до подтверждённого entitlement;

выдавать access по redirect вместо verified server-side payment webhook;

тихо пересчитывать старые результаты новой scoring-версией;

хранить психологическую логику в Telegram handlers;

терять прогресс при рестартах/ошибках;

позиционировать продукт как медицинскую или психиатрическую диагностику.

1\. Что строим

«Инструкция к себе» — Telegram-продукт глубокой структурированной психологической самодиагностики и персонального самопонимания.

Пользователь должен получить не 46 процентов и не типологический ярлык, а синтез:

что для него важно;

как регулируется самоценность;

как переносится неопределённость;

как принимаются решения;

где рвётся цепочка «хочу → выбрал → начал → продолжил → адаптировал»;

как строится близость;

как переживаются зависимость и автономия;

что происходит с эмоциями;

как работает избегание дискомфорта;

насколько цена ошибки ограничивает действия;

как человек проявляется;

как связаны достижения, признание и самоотношение;

что для него означают деньги;

какие конфликты подтверждаются данными;

какую функцию выполняют защитные стратегии;

какую цену они создают;

какие ресурсы уже доступны;

где находится главный рычаг изменения;

какие 10 персональных правил обращения с собой можно вывести из профиля.

До отдельной эмпирической валидации продукт позиционируется как комплексная система психологического самопонимания, не как «научно валидированный клинический тест».

2\. Бизнес-модель V1.3

Старая схема «175 взаимодействий → FREE → paywall» отменена.

Новая модель:

USER

→ /start

→ onboarding

→ consent

→ CORE: 24 mandatory

→ 0–6 adaptive

→ CORE analysis

→ FREE REPORT

→ personalized PAYWALL

→ PAYMENT

→ verified webhook

→ FULL entitlement / DEEP unlock

→ remaining assessment items

→ VFC

→ full deterministic scoring

→ 46 scales

→ patterns/conflicts/resources

→ FULL SYNTHESIS

→ 3–5 system cycles

→ 10 personal rules

→ FULL Telegram report

→ PDF

CORE продаёт не «расшифровку», а углубление исследования.

Маркетинговая задача CORE: дать высокое узнавание, один сильный инсайт и один реальный ресурс; честно показать границу знания и сформировать естественный вопрос «почему моя система устроена именно так?».

3\. Основные пути клиента

Новый

/start → onboarding → consent → CORE → FREE → paywall

Незавершённый CORE

/start → найти active session → resume с первого неотвеченного

CORE готов, не оплатил

/start → открыть FREE → paywall

Оплатил, DEEP не закончил

/start → entitlement → resume DEEP

FULL готов

/start → FULL / PDF / CORE hypothesis

Payment success + AI failure

Entitlement остаётся, повторная оплата запрещена.

PDF failure

Telegram FULL остаётся доступен.

Duplicate webhook

Один payment transition, один entitlement, одна логическая job-цепочка.

4\. Telegram UX

Один вопрос — одно сообщение/экран.

Inline keyboard.

Autosave после каждого ответа.

client\_event\_id для callback idempotency.

Разрешить изменить только последний ответ.

CORE: 24 обязательных, затем только реально нужные adaptive.

Progress bar/%, без демотивирующего акцента на огромном количестве вопросов.

Перед Q149–Q154 явно сказать: «следующие вопросы — о последних 14 днях».

VFC объяснить отдельно; left/right randomize.

Возвращающийся пользователь получает resume.

FREE и FULL читаются в Telegram.

PDF обязателен в paid FULL, но не является единственным способом прочитать отчёт.

Не использовать dark patterns.

5\. Версионирование

PRODUCT\_ARCHITECTURE\_VERSION=1.3

QUESTION\_BANK\_VERSION=1.2

CORE\_BANK\_VERSION=1.0

CORE\_ENGINE\_VERSION=1.0

CORE\_REPORT\_VERSION=1.0

DISPLAY\_ORDER\_VERSION=1.3

VFC\_VERSION=1.0

SCORING\_VERSION=1.2

PATTERN\_ENGINE\_VERSION=1.2

CONFLICT\_ENGINE\_VERSION=1.2

FULL\_SYNTHESIS\_ENGINE\_VERSION=1.0

REPORT\_SCHEMA\_VERSION=1.3

PROMPT\_VERSION=1.3

PDF\_TEMPLATE\_VERSION=1.1

PAYWALL\_VERSION=1.0

Начатая session заканчивается на своей версии. Новое прохождение = новая session и новый immutable analysis snapshot.

6\. Full assessment architecture

Q001–Q148: 46 primary trait scales.

Q149–Q154: anxiety\_state + low\_mood\_state; только modifiers.

Q155–Q160: context/moderators.

VFC01–VFC15: относительный выбор 6 ценностей.

Master maximum: 175 interactions.

CORE использует ссылки на существующие master IDs; после оплаты они не задаются повторно.

7\. 46 primary scales

cognitive\_openness

conscientiousness

extraversion

interpersonal\_accommodation

negative\_emotionality

recognition\_based\_self\_regulation

detachment\_tendency

rigid\_control\_tendency

experiential\_avoidance

intellectualization

emotional\_suppression

polarized\_evaluation

emotional\_awareness

attachment\_anxiety

attachment\_avoidance

interpersonal\_trust

boundary\_assertiveness

autonomy\_value

security\_value

achievement\_value

belonging\_value

meaning\_value

growth\_value

agency

self\_efficacy

external\_outcome\_attribution

uncertainty\_tolerance

control\_need

decisiveness

decision\_rumination

reassurance\_seeking

error\_intolerance

action\_initiation

adaptive\_flexibility

fear\_of\_evaluation

authentic\_expression

visibility\_desire

inner\_critic

vulnerability\_avoidance

performance\_based\_self\_worth

stable\_self\_worth

achievement\_drive

need\_awareness

money\_security

money\_autonomy

money\_status\_achievement

8\. Scoring primary scales

direct: scored\_answer = raw\_answer

reverse: scored\_answer = 8 - raw\_answer

raw\_mean = mean(scored\_items)

normalized\_score = ((raw\_mean - 1) / 6) \* 100

Высокий score всегда означает большую выраженность scale\_id.

profile\_median = median(46 normalized scores)

relative\_delta = normalized\_score - profile\_median

profile\_rank = rank among 46

within\_profile\_percent\_rank = within-person rank only

population\_percentile = null до реальных норм

Primary scale считается только при полном наборе своих items.

9\. Scale → items map

cognitive\_openness: Q001,Q002,Q003

conscientiousness: Q004,Q005,Q006(R)

extraversion: Q007,Q008,Q009

interpersonal\_accommodation: Q010,Q011,Q012(R)

negative\_emotionality: Q013,Q014,Q015(R),Q016

recognition\_based\_self\_regulation: Q017,Q018,Q019(R),Q020

detachment\_tendency: Q021,Q022,Q023(R)

rigid\_control\_tendency: Q024,Q025,Q026(R)

experiential\_avoidance: Q027,Q028,Q029(R),Q030

intellectualization: Q031,Q032,Q033(R)

emotional\_suppression: Q034,Q035,Q036(R)

polarized\_evaluation: Q037,Q038(R),Q039

emotional\_awareness: Q040,Q041,Q042(R)

attachment\_anxiety: Q043,Q044,Q045(R),Q046

attachment\_avoidance: Q047,Q048,Q049(R),Q050

interpersonal\_trust: Q051,Q052,Q053(R)

boundary\_assertiveness: Q054,Q055(R),Q056

autonomy\_value: Q057,Q058,Q059(R)

security\_value: Q060,Q061,Q062(R)

achievement\_value: Q063,Q064,Q065(R)

belonging\_value: Q066,Q067,Q068(R)

meaning\_value: Q069,Q070,Q071

growth\_value: Q072,Q073,Q074

agency: Q075,Q076(R),Q077,Q078

self\_efficacy: Q079,Q080(R),Q081

external\_outcome\_attribution: Q082,Q083,Q084(R)

uncertainty\_tolerance: Q085,Q086,Q087(R),Q088

control\_need: Q089,Q090,Q091(R)

decisiveness: Q092,Q093(R),Q094

decision\_rumination: Q095,Q096,Q097(R)

reassurance\_seeking: Q098,Q099,Q100(R)

error\_intolerance: Q101,Q102,Q103(R)

action\_initiation: Q104,Q105(R),Q106

adaptive\_flexibility: Q107,Q108(R),Q109

fear\_of\_evaluation: Q110,Q111,Q112(R),Q113

authentic\_expression: Q114,Q115,Q116(R),Q117

visibility\_desire: Q118,Q119,Q120(R)

inner\_critic: Q121,Q122,Q123(R)

vulnerability\_avoidance: Q124,Q125,Q126(R)

performance\_based\_self\_worth: Q127,Q128,Q129(R),Q130

stable\_self\_worth: Q131,Q132,Q133(R)

achievement\_drive: Q134,Q135,Q136(R)

need\_awareness: Q137,Q138,Q139(R)

money\_security: Q140,Q141,Q142(R)

money\_autonomy: Q143,Q144,Q145(R)

money\_status\_achievement: Q146,Q147,Q148(R)

10\. CORE BASE BANK V1.0 — 24 mandatory

C01 = Q018 recognition

C02 = Q019R recognition

C03 = Q028 avoidance

C04 = Q029R avoidance

C05 = Q043 attachment\_anxiety

C06 = Q045R attachment\_anxiety

C07 = Q047 attachment\_avoidance

C08 = Q049R attachment\_avoidance

C09 = Q076R agency

C10 = Q077 agency

C11 = Q085 uncertainty\_tolerance

C12 = Q087R uncertainty\_tolerance

C13 = Q104 action\_initiation

C14 = Q105R action\_initiation

C15 = Q112R fear\_of\_evaluation

C16 = Q113 fear\_of\_evaluation

C17 = Q114 authentic\_expression

C18 = Q116R authentic\_expression

C19 = Q128 performance\_based\_self\_worth

C20 = Q129R performance\_based\_self\_worth

C21 = Q131 stable\_self\_worth

C22 = Q133R stable\_self\_worth

C23 = Q138 need\_awareness

C24 = Q139R need\_awareness

11\. CORE signals

CS\_RECOGNITION

CS\_AVOIDANCE

CS\_ATTACH\_ANXIETY

CS\_ATTACH\_AVOIDANCE

CS\_AGENCY

CS\_UNCERTAINTY

CS\_ACTION

CS\_FEAR\_EVALUATION

CS\_AUTHENTICITY

CS\_PERFORMANCE\_WORTH

CS\_STABLE\_WORTH

CS\_NEED\_AWARENESS

Formula:

core\_signal\_raw = mean(two scored answers)

core\_signal = ((core\_signal\_raw - 1) / 6) \* 100

Это не полноценный primary scale score.

Provisional internal bands:

0–34 LOW

35–64 MID

65–100 HIGH

12\. CORE consistency/confidence

item\_gap = abs(scored\_item\_1 - scored\_item\_2)



0–1 CONSISTENT     confidence=0.80

2   ACCEPTABLE     confidence=0.70

3   UNCERTAIN      confidence=0.55

4–6 CONTRADICTORY confidence=0.35

После третьего adaptive item:

при согласованности confidence может подняться до 0.90;

при сохраняющемся большом разбросе cap 0.60.

13\. Adaptive pool

Recognition: Q017,Q020

Avoidance: Q027,Q030

Attachment anxiety: Q044,Q046

Attachment avoidance: Q048,Q050

Agency: Q075,Q078

Uncertainty: Q086,Q088

Action: Q106

Fear evaluation: Q110,Q111

Authenticity: Q115,Q117

Performance worth: Q127,Q130

Stable worth: Q132

Need awareness: Q137

Maximum adaptive = 6.

14\. Adaptive priority

adaptive\_priority =

&#x20;   0.35 \* uncertainty\_need

&#x20; + 0.30 \* conflict\_value

&#x20; + 0.25 \* report\_value

&#x20; + 0.10 \* coverage\_value

CONTRADICTORY=100

UNCERTAIN=70

ACCEPTABLE=25

CONSISTENT=0

После каждого adaptive answer пересчитать всё.

15\. Stop rule

Остановиться на 24, если:

есть сильный candidate с confidence >=0.70;

нет contradictory signal среди critical TOP findings;

вывод достаточно различим и reportable.

Продолжать, если:

top candidate неуверенный;

candidates почти равны;

critical signal contradictory;

adaptive question реально может изменить FREE conclusion.

Максимум 30.

16\. Human axes

ВНУТРЕННЯЯ ОПОРА → recognition + stable worth.

ДЕЙСТВИЕ В НЕОПРЕДЕЛЁННОСТИ → agency + uncertainty + action.

БЛИЗОСТЬ → attachment anxiety + avoidance.

ПРОЯВЛЕННОСТЬ → fear evaluation + authenticity.

САМОЦЕННОСТЬ → performance worth + stable worth.

КОНТАКТ С СОБОЙ → need awareness + avoidance.

Не превращать многомерные оси в бессмысленную одну цифру, если важнее конфигурация.

17\. CORE conflict engine

CF01 freedom\_without\_guarantees

= CS\_AGENCY \* inverse(CS\_UNCERTAINTY)/100

activation agency>=55



CF02 know\_but\_do\_not\_act

= CS\_NEED\_AWARENESS \*

&#x20; \[0.55\*inverse(CS\_ACTION)+0.45\*CS\_AVOIDANCE]/100



CF03 closeness\_dependency

= CS\_ATTACH\_ANXIETY \* CS\_ATTACH\_AVOIDANCE/100



CF04 authentic\_but\_costly

= CS\_FEAR\_EVALUATION \* CS\_AUTHENTICITY/100



CF05 self\_editing

= CS\_FEAR\_EVALUATION \* inverse(CS\_AUTHENTICITY)/100



CF06 prove\_worth

= CS\_PERFORMANCE\_WORTH \* inverse(CS\_STABLE\_WORTH)/100



CF07 need\_confirmation

= CS\_RECOGNITION \* inverse(CS\_STABLE\_WORTH)/100



CF08 know\_need\_avoid\_price

= CS\_NEED\_AWARENESS \* CS\_AVOIDANCE/100

inverse(x)=100-x.

Confidence:

geometric\_mean(input signal confidences)

Priority:

0.50\*conflict\_score

+0.30\*confidence\*100

+0.20\*distinctiveness

Если top score <50 или confidence <0.60 → CONFIGURATION\_ONLY.

18\. CORE resource engine

R01 adaptive\_agency

agency HIGH + uncertainty HIGH + action HIGH



R02 stable\_self\_worth

stable HIGH + performance LOW/MID



R03 secure\_relational\_capacity\_core

attach\_anxiety LOW + attach\_avoidance LOW



R04 free\_expression

fear LOW + authenticity HIGH



R05 contact\_with\_self

need\_awareness HIGH + avoidance LOW

19\. FREE report

Экран 0

Processing message: система сопоставляет ответы и проверяет выводы.

Экран 1 — «Ты в двух абзацах»

80–120 слов.

3–4 strongest reliable signals + top resource + top conflict + counter-evidence.

Экран 2 — Главный инсайт

Headline по CF.

Экран 3 — Как это работает

SIDE\_A → SIDE\_B → интеграция.

Экран 4 — Как это может проявляться

3–4 разрешённых manifestations, conditional language.

Экран 5 — Твоя опора

Top resource и его связь с conflict.

Экран 6 — Граница знания

«Мы уже видим ЧТО, но пока не знаем ПОЧЕМУ».

Показать несколько возможных differentiators, которые измерит DEEP, но не утверждать ни один без данных.

20\. CORE headline templates

CF01: ТЫ ХОЧЕШЬ СВОБОДЫ, НО ХОЧЕШЬ ГАРАНТИЙ.

CF02: ТЫ ЗНАЕШЬ, ЧЕГО ХОЧЕШЬ. НО ЭТО ЕЩЁ НЕ ЗНАЧИТ, ЧТО ТЫ ЭТО ВЫБЕРЕШЬ.

CF03: ТЫ ХОЧЕШЬ БЛИЗОСТИ, НО НЕ ХОЧЕШЬ ЗАВИСЕТЬ.

CF04: ТЫ ОСТАЁШЬСЯ СОБОЙ. НО ИНОГДА ЭТО СЛИШКОМ ДОРОГО.

CF05: ТЫ РЕДАКТИРУЕШЬ СЕБЯ ЕЩЁ ДО ТОГО, КАК ЭТО СДЕЛАЮТ ДРУГИЕ.

CF06: ТЕБЕ НЕДОСТАТОЧНО БЫТЬ. ТЕБЕ НУЖНО ДОКАЗЫВАТЬ, ЧТО ТЫ ЧЕГО-ТО СТОИШЬ.

CF07: ТЕБЕ ЛЕГЧЕ ВЕРИТЬ В СЕБЯ, КОГДА В ТЕБЯ ВЕРЯТ ДРУГИЕ.

CF08: ТЫ ЗНАЕШЬ, ЧЕГО ХОЧЕШЬ. ТЫ ПРОСТО НЕ ВСЕГДА ГОТОВ ПЛАТИТЬ ЦЕНУ.

21\. Paywall

Не «купить полную версию теста».

Смысловой каркас:

ЭТО БЫЛА НЕ ИНСТРУКЦИЯ.

ЭТО БЫЛА ПЕРВАЯ СТРАНИЦА.



Короткая диагностика показала наиболее заметную конфигурацию.

Полная «Инструкция к себе» показывает,

как разные части твоей системы связаны между собой.

Locked value:

архитектура;

ценности;

эмоции;

отношения;

решения;

действие;

проявленность;

самоценность;

деньги;

current context/state;

3–5 system cycles;

10 personal rules;

resource/trap/leverage.

CTA:

ПОЛУЧИТЬ ПОЛНУЮ ИНСТРУКЦИЮ

Подпись:

Твои ответы уже сохранены. Начинать заново не придётся.

22\. Payment/entitlement

PAYMENT\_CREATE

→ checkout

→ verified provider webhook

→ payment=PAID

→ entitlement FULL\_REPORT

→ phase=DEEP\_UNLOCKED

Оплата и entitlement — разные entities.

Sources:

payment

promo

manual grant

bundle

Sirius

internal test

Success redirect не даёт access.

23\. DEEP

После оплаты:

взять answered master IDs;

взять canonical master order;

исключить уже отвеченные CORE/adaptive IDs;

задать оставшиеся trait questions;

state/context;

VFC;

lock raw answers;

full analysis.

24\. VFC values engine

forced\_choice\_wins = selected count out of 5

relative\_choice\_priority = wins/5\*100

Не усреднять absolute value score и forced-choice priority.

Две высокие ценности не равны конфликту автоматически.

25\. Current state

anxiety\_state = mean(Q149,Q150,Q151) normalized

low\_mood\_state = mean(Q152,Q153,Q154) normalized

Sensitive to anxiety:

negative\_emotionality

uncertainty\_tolerance

control\_need

attachment\_anxiety

decision\_rumination

fear\_of\_evaluation

error\_intolerance

Sensitive to low mood:

self\_efficacy

agency

action\_initiation

achievement\_drive

stable\_self\_worth

need\_awareness

State не меняет trait score; только interpretation caution.

26\. Context

Q155 relational\_uncertainty

Q156 support\_type

Q157 evaluation\_source

Q158 stakes\_sensitive\_control

Q159 financial\_baseline\_security

Q160 current\_meaning

Context не входит в primary averages.

27\. Response quality

completion\_ratio

median\_response\_time\_ms

response\_time\_distribution

longest\_identical\_run

straightlining\_flag

answer\_variance

extreme\_response\_ratio

acquiescence\_index

direct\_reverse\_disagreement\_flags

Не использовать lie\_score/honesty\_score.

HIGH 1.00

ACCEPTABLE 0.90

CAUTION 0.75

LOW 0.55

item\_spread >=5 → HETEROGENEOUS\_SCALE\_RESPONSES; scale\_confidence\*=0.90

28\. Full pattern engine — 37 patterns

SELF\_WORTH

P01 achievement\_contingent\_self\_worth

=.45 performance\_based\_self\_worth

+.25 achievement\_drive

+.20 inner\_critic

+.10 inverse(stable\_self\_worth)



P02 externalized\_self\_validation

=.50 recognition\_based\_self\_regulation

+.25 reassurance\_seeking

+.25 inverse(stable\_self\_worth)



P03 harsh\_internal\_regulation

=.50 inner\_critic

+.25 error\_intolerance

+.25 conscientiousness

activation inner\_critic>=55



P04 stable\_self\_regard RESOURCE

=.55 stable\_self\_worth

+.25 inverse(performance\_based\_self\_worth)

+.20 inverse(recognition\_based\_self\_regulation)

EMOTIONAL\_REGULATION

P05 experiential\_avoidance\_loop

=.55 experiential\_avoidance

+.20 negative\_emotionality

+.15 inverse(emotional\_awareness)

+.10 inverse(adaptive\_flexibility)



P06 intellectualized\_emotion

=intellectualization \*

\[.40 experiential\_avoidance

+.30 emotional\_suppression

+.30 inverse(emotional\_awareness)]/100

suppress if awareness>=70 AND avoidance<=35



P07 emotional\_concealment

=.45 emotional\_suppression

+.35 vulnerability\_avoidance

+.20 fear\_of\_evaluation



P08 emotionally\_informed\_regulation RESOURCE

=.45 emotional\_awareness

+.30 inverse(experiential\_avoidance)

+.25 adaptive\_flexibility

RELATIONSHIPS

P09 attachment\_hyperactivation

=.50 attachment\_anxiety

+.25 reassurance\_seeking

+.15 relational\_uncertainty\_context

+.10 negative\_emotionality



P10 defensive\_independence

=autonomy\_value \*

\[.45 attachment\_avoidance

+.30 vulnerability\_avoidance

+.25 detachment\_tendency]/100

do not infer from autonomy alone



P11 approach\_avoidance\_closeness

=attachment\_anxiety\*attachment\_avoidance/100



P12 self\_loss\_through\_accommodation

=\[.40 belonging+.30 attachment\_anxiety+.30 accommodation]

\*

\[.55 inverse(boundary\_assertiveness)+.45 inverse(authentic\_expression)]

/100

suppress boundaries>=70



P13 secure\_relational\_capacity RESOURCE

=.30 trust

+.25 boundaries

+.20 inverse(attachment\_anxiety)

+.15 inverse(attachment\_avoidance)

+.10 inverse(vulnerability\_avoidance)

NEEDS\_BOUNDARIES

P14 need\_disconnection

=.50 inverse(need\_awareness)

+.25 accommodation

+.25 inverse(boundaries)



P15 needs\_to\_action\_gap

=need\_awareness \*

\[.35 inverse(action\_initiation)

+.25 fear\_of\_evaluation

+.20 experiential\_avoidance

+.20 inverse(boundaries)]/100

AGENCY\_ACTION

P16 learned\_powerlessness\_configuration

=.35 inverse(agency)

+.30 inverse(self\_efficacy)

+.20 external\_outcome\_attribution

+.15 inverse(action\_initiation)

suppress if agency>=70



P17 agency\_without\_confidence

=agency\*inverse(self\_efficacy)/100



P18 confidence\_without\_action

=self\_efficacy\*inverse(action\_initiation)/100



P19 certainty\_before\_action

=.40 inverse(uncertainty\_tolerance)

+.30 control\_need

+.30 error\_intolerance



P20 action\_without\_adaptation

=action\_initiation\*inverse(adaptive\_flexibility)/100



P21 adaptive\_agency RESOURCE

=.35 agency+.25 action\_initiation+.25 adaptive\_flexibility+.15 self\_efficacy

DECISIONS

P22 analysis\_paralysis

=.40 inverse(decisiveness)

+.30 decision\_rumination

+.20 error\_intolerance

+.10 inverse(uncertainty\_tolerance)



P23 outsourced\_certainty

=.45 reassurance\_seeking

+.25 inverse(stable\_self\_worth)

+.20 fear\_of\_evaluation

+.10 inverse(self\_efficacy)



P24 post\_decision\_instability

=.55 decision\_rumination

+.25 error\_intolerance

+.20 reassurance\_seeking

VISIBILITY

P25 visibility\_conflict

=visibility\_desire \*

\[.50 fear\_of\_evaluation

+.30 inverse(authentic\_expression)

+.20 vulnerability\_avoidance]/100

suppress if visibility\_desire<40



P26 self\_editing\_for\_acceptance

=.45 inverse(authentic\_expression)

+.30 fear\_of\_evaluation

+.25 recognition\_based\_self\_regulation



P27 visible\_but\_vulnerable

=visibility\_desire\*fear\_of\_evaluation\*authentic\_expression/10000

resource-tension, not avoidance



P28 low\_visibility\_by\_preference NORMALIZING

=inverse(visibility\_desire)\*inverse(fear\_of\_evaluation)/100

ACHIEVEMENT

P29 healthy\_achievement\_orientation RESOURCE

=.40 achievement\_drive

+.25 achievement\_value

+.20 stable\_self\_worth

+.15 adaptive\_flexibility

downgrade if performance worth high \& stable worth low



P30 achievement\_pressure

=.35 achievement\_drive

+.30 performance\_based\_self\_worth

+.20 inner\_critic

+.15 error\_intolerance

downgrade if stable\_self\_worth>=75 AND inner\_critic<=40



P31 perfectionistic\_evaluation

=.30 error\_intolerance

+.25 polarized\_evaluation

+.20 inner\_critic

+.15 rigid\_control\_tendency

+.10 fear\_of\_evaluation

do not call clinical perfectionism

MONEY

P32 money\_as\_safety\_regulator

=.60 money\_security+.20 security\_value+.20 control\_need

if financial\_baseline\_security<=3:

contextual concern, not defensive dependence



P33 money\_as\_autonomy\_regulator

=.55 money\_autonomy+.25 autonomy\_value+.20 agency



P34 financial\_success\_identity

=.50 money\_status\_achievement

+.25 achievement\_value

+.15 recognition\_based\_self\_regulation

+.10 performance\_based\_self\_worth

suppress if money\_status\_achievement<40

VALUES\_MEANING

P35 meaning\_gap

=meaning\_value\*inverse(current\_meaning\_normalized)/100



P36 growth\_stability\_tension

=growth\_value\*security\_value/100

potential tension; conflict needs uncertainty/flexibility/VFC support



P37 autonomy\_belonging\_tension

=autonomy\_value\*belonging\_value/100

potential tension; needs attachment/boundary/defensive-independence/VFC support

29\. Full conflict engine — 12 conflicts

C01 visibility\_vs\_evaluation

= visibility\_desire \* fear\_of\_evaluation /100

support: low authenticity



C02 authenticity\_vs\_acceptance

= \[.60 autonomy+.40 authenticity] \*

&#x20; \[.55 recognition\_regulation+.45 fear\_evaluation]/100

low authenticity supports; avoid double counting



C03 closeness\_vs\_dependency

= \[.55 belonging+.45 attachment\_anxiety] \*

&#x20; \[.60 attachment\_avoidance+.40 vulnerability\_avoidance]/100

two active sides required



C04 belonging\_vs\_boundaries

= \[.60 belonging+.40 accommodation] \*

&#x20; inverse(boundary\_assertiveness)/100



C05 achievement\_vs\_failure

= \[.50 achievement\_value+.50 achievement\_drive] \*

&#x20; \[.55 error\_intolerance+.45 performance\_self\_worth]/100



C06 action\_vs\_certainty

= \[.45 agency+.30 action\_initiation+.25 achievement\_drive] \*

&#x20; \[.50 inverse(uncertainty)+.30 control+.20 error\_intolerance]/100



C07 choice\_vs\_error

= \[.50 decisiveness+.30 agency+.20 autonomy] \*

&#x20; error\_intolerance/100



C08 need\_vs\_expression

= need\_awareness \*

&#x20; \[.55 inverse(boundaries)+.45 inverse(authenticity)]/100



C09 growth\_vs\_security

= growth\_value\*security\_value/100

default POTENTIAL\_VALUE\_TENSION

conflict only with VFC/uncertainty/control support



C10 autonomy\_vs\_belonging

= autonomy\_value\*belonging\_value/100

default POTENTIAL\_VALUE\_TENSION

requires boundary/attachment/defensive-independence/VFC support



C11 money\_freedom\_vs\_money\_safety

= money\_autonomy\*money\_security/100

financial baseline modifies interpretation



C12 meaning\_vs\_current\_life

= meaning\_gap

30\. Mandatory suppression/counter-evidence

visibility\_conflict:

suppress if visibility\_desire<40



intellectualized\_emotion:

suppress if emotional\_awareness>=70 AND experiential\_avoidance<=35



learned\_powerlessness\_configuration:

suppress if agency>=70



money\_as\_safety\_regulator:

if financial\_baseline\_security<=3

do not infer defensive money function



achievement\_pressure:

downgrade if stable\_self\_worth>=75 AND inner\_critic<=40



self\_loss\_through\_accommodation:

suppress if boundary\_assertiveness>=70

Counter-evidence хранить рядом с finding и всегда передавать synthesis/report engine.

31\. Clusters / priority

SELF\_WORTH

EMOTIONAL\_REGULATION

RELATIONSHIPS

NEEDS\_BOUNDARIES

AGENCY\_ACTION

DECISIONS

VISIBILITY\_EVALUATION

ACHIEVEMENT

MONEY

VALUES\_MEANING

Base priority:

priority\_score =

pattern\_score

\* confidence

\* interpretation\_weight

\* uniqueness\_factor

\* current\_relevance\_factor

Weights:

CORE\_MECHANISM=1.00

IMPORTANT=.85

RESOURCE=.80

CONTEXTUAL=.70

MODERATOR=.60

NORMALIZING=.55

32\. FULL SYNTHESIS ENGINE V1.0

Главная задача: не показать 46 scales, а найти минимальное число системных объяснений, покрывающих максимум данных.

Evidence hierarchy

LEVEL A DIRECT — измеренный construct.

LEVEL B COMPOSITE — подтверждённый pattern/conflict.

LEVEL C SYNTHESIS — несколько независимых findings образуют общую систему.

LEVEL D HYPOTHESIS — возможное объяснение; только cautious language.

Finding data model

id:

domain:

type:

score:

status:

confidence:

priority:

evidence: \[]

counter\_evidence: \[]

context\_modifiers: \[]

state\_modifiers: \[]

possible\_functions: \[]

possible\_costs: \[]

resources: \[]

allowed\_inferences: \[]

forbidden\_inferences: \[]

33\. System cycle builder

TRIGGER

→ APPRAISAL

→ REGULATION

→ BEHAVIOR

→ SHORT-TERM FUNCTION

→ LONG-TERM COST

Cycle разрешён только если:

>=1 подтверждённый trigger/appraisal;

>=1 regulation pattern;

>=1 behavioral consequence;

>=3 independent primary scales;

желательно >=2 domains.

Иначе не строить причинную цепочку.

34\. Systemicity

systemicity\_score =

.30 evidence\_strength

+.25 explanatory\_coverage

+.20 confidence

+.15 cross\_domain\_relevance

+.10 actionable\_value

Выбрать 3–5 cycles.

35\. Redundancy penalty

Если новый cycle покрывает >60% тех же evidence nodes, что уже выбранный:

merge;

либо downgrade.

36\. Resource engine FULL

Каждый resource:

resource\_strength

confidence

availability

Важно различать «ресурс существует» и «ресурс доступен в текущей конфигурации».

37\. Resource × conflict

Для каждого TOP cycle найти уже существующий ресурс, который может его размыкать.

Это должно быть backend-supported.

38\. CORE→DEEP revision

Хранить original CORE hypothesis.

После FULL:

CONFIRMED

REFINED

NOT\_SUPPORTED

FULL должен прямо объяснять:

«В короткой версии мы предположили X. После полной диагностики Y».

NOT\_SUPPORTED — валидный хороший результат, а не ошибка.

39\. Personal rule engine

Backend формирует rule candidates.

Типы:

SELF\_OBSERVATION

BEHAVIORAL\_EXPERIMENT

DECISION\_RULE

RELATIONAL\_RULE

ENVIRONMENT\_RULE

REFLECTION\_PROMPT

PROFESSIONAL\_SUPPORT\_OPTION

Каждое правило проходит:

RELEVANCE

FEASIBILITY

NON\_CONTRADICTION

40\. TOP\_RESOURCE / TOP\_TRAP / TOP\_LEVERAGE

TOP\_RESOURCE = strongest available resource

TOP\_TRAP = most systemic limiting cycle

TOP\_LEVERAGE = maximum downstream change potential

leverage\_score =

systemicity \* actionability \* resource\_support

41\. FULL report structure

1\. Ты в целом

Executive summary, architecture, drivers, limitations, main conflict, resource, leverage.

2\. Что тобой управляет

Values + VFC + tensions.

3\. Как ты обходишься с собой

Self-worth, recognition, inner critic, achievement.

4\. Что ты делаешь с чувствами

Awareness, avoidance, suppression, intellectualization, flexibility, function/cost.

5\. Как ты любишь

Anxiety, avoidance, trust, boundaries, closeness, vulnerability.

6\. Как ты принимаешь решения

Before/during/after decision; rumination; reassurance; error; uncertainty; control.

7\. Как ты меняешь свою жизнь

Agency, efficacy, initiation, flexibility, attribution, exact break in action chain.

8\. Как ты показываешь себя миру

Visibility desire, fear, authenticity, recognition; distinguish preference from avoidance.

9\. Что для тебя значат деньги

Safety, autonomy, status/achievement + Q159.

10\. Ты под нагрузкой

State modifiers and caution.

11\. Твоя система

3–5 cycles + function/cost + resources.

12\. Твоя инструкция

10 personal rules.

Финал

твоя опора;

твоя ловушка;

твой рычаг.

42\. OpenAI/LLM contract

LLM backend-side only. API key server-side. Model name in config.

LLM запрещено:

пересчитывать scores;

добавлять unknown findings;

менять thresholds;

диагностировать;

объяснять детством/травмой без данных;

игнорировать counter-evidence;

раскрывать formulas/internal IDs;

выдавать population language;

раскрывать FULL в FREE;

придумывать биографию.

LLM разрешено:

естественно объяснять backend findings;

синтезировать разрешённые claims;

писать по-русски прямо, умно, психологически грамотно;

использовать cautious language в зависимости от confidence.

43\. CORE LLM input

{

&#x20; "meta":{"product\_version":"1.3","generation\_mode":"CORE\_FREE","language":"ru"},

&#x20; "core\_signals":\[],

&#x20; "signal\_confidence":\[],

&#x20; "human\_axes":\[],

&#x20; "top\_conflict":{},

&#x20; "secondary\_conflicts":\[],

&#x20; "top\_resource":{},

&#x20; "evidence\_items":\[],

&#x20; "counter\_evidence":\[],

&#x20; "adaptive\_questions\_used":\[],

&#x20; "overall\_core\_confidence":0.0,

&#x20; "report\_mode":"CONFLICT|CONFIGURATION\_ONLY"

}

44\. FULL LLM input

{

&#x20; "meta":{"assessment\_version":"1.3","generation\_mode":"FULL","language":"ru"},

&#x20; "response\_quality":{},

&#x20; "state":{},

&#x20; "contexts":{},

&#x20; "value\_structure":{},

&#x20; "primary\_scales":{},

&#x20; "active\_patterns":\[],

&#x20; "active\_conflicts":\[],

&#x20; "system\_cycles":\[],

&#x20; "resources":\[],

&#x20; "resource\_cycle\_matches":\[],

&#x20; "core\_revision":{

&#x20;   "original\_hypothesis":{},

&#x20;   "status":"CONFIRMED|REFINED|NOT\_SUPPORTED",

&#x20;   "refined\_hypothesis":{}

&#x20; },

&#x20; "chapter\_findings":{},

&#x20; "personal\_rule\_candidates":\[],

&#x20; "top\_resource":{},

&#x20; "top\_trap":{},

&#x20; "top\_leverage":{},

&#x20; "forbidden\_inferences":\[],

&#x20; "interpretation\_cautions":\[]

}

45\. LLM validation

JSON\_SCHEMA\_VALID

ALL\_REQUIRED\_FIELDS\_PRESENT

ALL\_EVIDENCE\_IDS\_EXIST

NO\_UNKNOWN\_FINDING\_IDS

NO\_FULL\_FIELDS\_IN\_FREE

NO\_EMPTY\_CRITICAL\_SECTION

NO\_UNSUPPORTED\_CAUSALITY

NO\_DIAGNOSIS\_LANGUAGE

NO\_INTERNAL\_FORMULAS\_EXPOSED

NO\_POPULATION\_PERCENTILE\_LANGUAGE\_WITHOUT\_NORMS

CORE\_CONFIDENCE\_LANGUAGE\_MATCH

COUNTER\_EVIDENCE\_RESPECTED

Persistent generation failure не уничтожает analysis snapshot.

Unique generation key:

analysis\_run\_id + report\_type + report\_version.

46\. PDF

VALIDATED\_FULL\_REPORT\_JSON

→ TEMPLATE

→ RENDERER

→ PRIVATE FILE

→ TELEGRAM sendDocument

PDF не делает отдельный AI-analysis.

Включить:

product title;

date;

report/assessment versions;

user-facing chapters;

10 rules;

disclaimer.

Не включать:

IDs;

formulas;

prompt;

hidden thresholds/confidence.

47\. Backend architecture

Разделить:

telegram-adapter

application/service

assessment engine

core engine

scoring engine

pattern engine

conflict engine

synthesis engine

report service

payment service

entitlement service

pdf service

analytics

admin

persistence

job workers

Telegram handler не хранит psych logic.

48\. Suggested API

POST /session/start

GET  /session/{id}

POST /session/{id}/consent

GET  /assessment/{session}/next

POST /assessment/{session}/answer

POST /assessment/{session}/change-last

GET  /assessment/{session}/progress

POST /core/{session}/evaluate

GET  /report/{session}/free

POST /payment/create

POST /payment/webhook

GET  /entitlement/{session}

POST /deep/{session}/start

POST /assessment/{session}/complete

POST /analysis/{session}/run

GET  /analysis/{session}/status

GET  /report/{session}/full

POST /report/{session}/retry

GET  /pdf/{analysis\_run}/status

POST /pdf/{analysis\_run}/retry

GET  /pdf/{analysis\_run}/download

POST /user/data-delete-request

49\. Database

users

id, telegram\_user\_id, chat\_id, language, timestamps, deleted\_at

consents

user\_id, consent\_version, accepted\_at, metadata

assessment\_sessions

user\_id, versions, phase, status, current\_position, core\_completed\_at, paid\_at, deep\_completed\_at, timestamps

questions

question\_id, scale\_id, direction, type, text\_ru, version, active

answers

session\_id, question\_id, raw\_answer, phase\_answered, response\_time\_ms, display\_position, client\_event\_id, timestamps

core\_analysis

session\_id, core\_engine\_version, signals\_json, conflicts\_json, resources\_json, adaptive\_history\_json, top\_conflict\_id, top\_resource\_id, confidence, report\_mode, input\_hash

vfc\_pairs / vfc\_answers

analysis\_runs

session\_id, engine\_versions\_json, input\_hash, immutable\_profile\_snapshot\_json, status

scale\_scores

analysis\_run\_id, scale\_id, raw\_mean, normalized, rank, delta, confidence, flags

findings

analysis\_run\_id, finding\_id, type, cluster, score, status, confidence, priority, evidence\_json, counter\_evidence\_json, metadata\_json

system\_cycles

analysis\_run\_id, cycle\_id, systemicity\_score, confidence, trigger/appraisal/regulation/behavior/function/cost/evidence/resource\_matches

reports

analysis\_run\_id/session\_id, report\_type, prompt/schema/model versions, report\_json, generation\_status

pdf\_exports

products

payments

access\_entitlements

analytics\_events

admin\_audit\_log

50\. State machine V1.3

CREATED

→ CONSENT\_PENDING

→ CORE\_IN\_PROGRESS

→ CORE\_EVALUATING

→ CORE\_READY

→ PAYWALL

→ PAYMENT\_PENDING

→ DEEP\_UNLOCKED

→ DEEP\_IN\_PROGRESS

→ VFC\_IN\_PROGRESS

→ FULL\_ASSESSMENT\_COMPLETED

→ SCORING

→ SCORED

→ FULL\_SYNTHESIS

→ FULL\_GENERATING

→ FULL\_READY

→ PDF\_GENERATING

→ COMPLETE

Errors:

CORE\_GENERATION\_FAILED

PAYMENT\_FAILED

SCORING\_FAILED

FULL\_GENERATION\_FAILED

PDF\_GENERATION\_FAILED

51\. Idempotency/concurrency

unique client\_event\_id;

duplicate callback safe;

payment webhook idempotent;

report/PDF jobs idempotent;

race-safe state transitions;

job deduplication;

database transaction around consequential transitions.

52\. Admin

Dashboard metrics:

started;

CORE completion;

average CORE length;

adaptive distribution;

FREE views;

paywall;

payment;

DEEP completion;

FULL;

PDF;

conversions;

drop-offs.

Allowed:

retry reports/PDF;

grant/revoke entitlement;

inspect errors;

data deletion.

Не разрешать manually edit raw answers/scores.

53\. Analytics events

BOT\_STARTED

ONBOARDING\_VIEWED

CONSENT\_ACCEPTED

CORE\_STARTED

CORE\_QUESTION\_ANSWERED

CORE\_BASE\_COMPLETED

CORE\_ADAPTIVE\_STARTED

CORE\_ADAPTIVE\_QUESTION\_ANSWERED

CORE\_COMPLETED

CORE\_ANALYSIS\_STARTED

CORE\_REPORT\_READY

CORE\_REPORT\_VIEWED

PAYWALL\_VIEWED

PAYMENT\_STARTED

PAYMENT\_SUCCEEDED

PAYMENT\_FAILED

DEEP\_STARTED

DEEP\_QUESTION\_ANSWERED

DEEP\_BREAK\_REACHED

DEEP\_RESUMED

DEEP\_COMPLETED

VFC\_STARTED

VFC\_COMPLETED

FULL\_ANALYSIS\_STARTED

FULL\_ANALYSIS\_READY

FULL\_REPORT\_STARTED

FULL\_REPORT\_READY

FULL\_REPORT\_VIEWED

PDF\_STARTED

PDF\_READY

PDF\_SENT

PDF\_FAILED

CORE\_REVISION\_CONFIRMED

CORE\_REVISION\_REFINED

CORE\_REVISION\_NOT\_SUPPORTED

54\. Pilot export

Без Telegram ID:

anonymous\_subject\_id;

versions;

all answers;

adaptive selection + reasons;

response times;

quality;

CORE signals/conflicts;

scale scores;

patterns/conflicts;

state/context;

cycles;

completion/conversion.

Использовать для psychometric calibration и продуктовой аналитики.

55\. Privacy/security

data minimization;

identity separated from assessment by internal ID;

TLS;

restricted DB;

secrets outside repo;

least privilege;

protected backups;

no psychological plaintext in normal logs;

deletion flow;

audit destructive actions;

private PDF storage;

isolated LOCAL/STAGING/PRODUCTION.

56\. Feature flags

ACTIVE\_PRODUCT\_VERSION

ENABLE\_CORE

ENABLE\_CORE\_ADAPTIVE

ENABLE\_PAYMENTS

ENABLE\_DEEP

ENABLE\_FULL\_REPORT

ENABLE\_PDF

ENABLE\_PROMO

ENABLE\_BREAK\_SCREENS

ENABLE\_ADMIN

ENABLE\_NEW\_SYNTHESIS\_ENGINE

57\. Observability

structured safe logs;

metrics;

error tracking;

worker monitoring;

payment alerts;

report/PDF failure alerts;

backup monitoring;

health endpoints;

audit trail.

58\. Unit tests

direct raw=1 →1

reverse raw=1 →7

all score 4 →50

all score 7 →100

all score 1 →0

state never alters primary

context never enters primary averages

VFC 4 wins/5 →80

CORE:

reverse;

gap/confidence;

adaptive;

max six;

stop at 24;

geometric confidence;

conflict threshold fallback.

59\. Golden profiles

high agency / low confidence

visibility conflict

visible but vulnerable

low visibility by preference

secure relational capacity

attachment approach-avoidance

achievement pressure

healthy achievement

defensive independence

meaning gap

high current anxiety

money safety under real insecurity

needs understood but not enacted

high emotional awareness + high avoidance

confidence without action

action without adaptation

stable self-worth + high achievement drive

CORE freedom-without-guarantees

CORE self-editing

CORE prove-worth

CORE no dominant conflict

CORE contradictory → adaptive

CORE REFined by DEEP

CORE NOT\_SUPPORTED by DEEP

60\. E2E acceptance

Happy:

start→consent→CORE→adaptive→FREE→paywall→payment→DEEP→VFC→FULL→PDF→restart/access persists

Также:

resume CORE;

resume DEEP;

payment failure;

payment success + LLM failure;

duplicate webhook;

PDF failure;

version transition;

unauthorized FULL;

data deletion.

61\. Definition of Done

MVP готов, только если:

CORE 24.

Adaptive 0–6.

CORE deterministic analysis.

FREE.

Personalized paywall.

Verified payment/entitlement.

DEEP without repeat CORE IDs.

Master Q001–Q160.

VFC01–15.

46 scales.

state/context/quality.

37 patterns +12 conflicts.

suppression/counter.

3–5 synthesis cycles.

CORE revision.

personal rules.

FULL Telegram.

PDF.

autosave/resume/idempotency.

admin/analytics/security/versioning.

62\. Not required in MVP

mobile app;

complex CRM;

population norms;

clinical diagnosis;

therapist marketplace;

ML adaptive testing;

longitudinal UI;

complex 46-scale charts;

multilingual.

63\. Machine-readable config package

questions\_v1\_2.json

scales\_v1\_2.json

core\_bank\_v1\_0.json

core\_adaptive\_pool\_v1\_0.json

core\_conflicts\_v1\_0.json

core\_resources\_v1\_0.json

core\_report\_templates\_v1\_0.json

display\_order\_v1\_3.json

vfc\_v1\_0.json

patterns\_v1\_2.json

conflicts\_v1\_2.json

suppression\_rules\_v1\_2.json

system\_cycle\_rules\_v1\_0.json

resource\_rules\_v1\_0.json

rule\_candidates\_v1\_0.json

report\_schema\_v1\_3.json

core\_prompt\_v1\_0.txt

full\_prompt\_v1\_3.txt

paywall\_templates\_v1\_0.json

pdf\_template\_v1\_1/

64\. Product tone

direct;

intelligent;

psychologically literate;

non-mystical;

non-generic;

no infantilization;

no moralizing;

no pathology where preference/context explains behavior;

strong wording allowed only when evidence supports it.

APPENDIX A. CANONICAL MASTER QUESTION BANK Q001–Q160

Ниже вопросы извлечены из утверждённого QUESTION\_BANK\_V1.2. Формулировки нельзя менять без создания новой версии question bank.

Q001 — `cognitive\_openness` · `D` · `TRAIT`

Мне интересно разбираться в идеях, которые заставляют по-новому смотреть на привычные вещи.

Q002 — `cognitive\_openness` · `D` · `TRAIT`

Мне интересно рассматривать одну и ту же тему с разных, иногда противоречащих друг другу сторон.

Q003 — `cognitive\_openness` · `D` · `TRAIT`

Мне нравится находить неожиданные связи между разными идеями.

Q004 — `conscientiousness` · `D` · `TRAIT`

Если я беру на себя задачу, я стараюсь довести её до конца.

Q005 — `conscientiousness` · `D` · `TRAIT`

Я умею выстраивать порядок действий, когда цель требует длительной работы.

Q006 — `conscientiousness` · `R` · `TRAIT`

Мне трудно придерживаться плана, даже если он для меня важен.

Q007 — `extraversion` · `D` · `TRAIT`

Общение с людьми часто даёт мне дополнительную энергию.

Q008 — `extraversion` · `D` · `TRAIT`

Мне легко первым вступить в разговор или познакомиться.

Q009 — `extraversion` · `D` · `TRAIT`

В группе мне естественно занимать активную позицию.

Q010 — `interpersonal\_accommodation` · `D` · `TRAIT`

Даже в конфликте я стараюсь понять, что происходит с другим человеком.

Q011 — `interpersonal\_accommodation` · `D` · `TRAIT`

При разногласиях я обычно ищу вариант, в котором учтены интересы обеих сторон.

Q012 — `interpersonal\_accommodation` · `R` · `TRAIT`

Если я считаю свою позицию правильной, я могу продолжать настаивать на ней, даже когда это усиливает конфликт.

Q013 — `negative\_emotionality` · `D` · `TRAIT`

Неприятные события могут надолго выбивать меня из внутреннего равновесия.

Q014 — `negative\_emotionality` · `D` · `TRAIT`

Я довольно быстро начинаю тревожиться, когда ситуация становится напряжённой.

Q015 — `negative\_emotionality` · `R` · `TRAIT`

Даже при серьёзных проблемах мне обычно легко сохранять эмоциональное спокойствие.

Q016 — `negative\_emotionality` · `D` · `TRAIT`

Я часто заранее прокручиваю, что может пойти не так.

Q017 — `recognition\_based\_self\_regulation` · `D` · `TRAIT`

Когда мои усилия остаются незамеченными, мне бывает труднее чувствовать удовлетворение от результата.

Q018 — `recognition\_based\_self\_regulation` · `D` · `TRAIT`

Отсутствие отклика на то, что для меня важно, может заставить меня сомневаться в себе.

Q019 — `recognition\_based\_self\_regulation` · `R` · `TRAIT`

Если важный для меня результат не получает одобрения окружающих, я всё равно обычно способен считать его ценным.

Q020 — `recognition\_based\_self\_regulation` · `D` · `TRAIT`

Если другой человек получает больше признания за сопоставимый результат, это может заметно задевать меня.

Q021 — `detachment\_tendency` · `D` · `TRAIT`

Когда от меня ждут очень большой эмоциональной вовлечённости, мне иногда хочется увеличить дистанцию.

Q022 — `detachment\_tendency` · `D` · `TRAIT`

Мне комфортнее самостоятельно перерабатывать значительную часть переживаний, чем делиться ими даже с близкими.

Q023 — `detachment\_tendency` · `R` · `TRAIT`

Даже при очень тесной близости мне обычно комфортно оставаться эмоционально включённым в отношения.

Q024 — `rigid\_control\_tendency` · `D` · `TRAIT`

Мне трудно работать спокойно, если важный процесс организован хаотично или непоследовательно.

Q025 — `rigid\_control\_tendency` · `D` · `TRAIT`

Мне бывает трудно принять способ выполнения задачи, который отличается от моего, даже если результат получается приемлемым.

Q026 — `rigid\_control\_tendency` · `R` · `TRAIT`

Если привычный порядок нарушается, я обычно довольно быстро нахожу другой удобный способ действовать.

Q027 — `experiential\_avoidance` · `D` · `TRAIT`

Сильный внутренний дискомфорт часто заставляет меня быстро менять ситуацию, даже если объективно можно было бы ничего не делать.

Q028 — `experiential\_avoidance` · `D` · `TRAIT`

Я могу откладывать важные действия, если они вызывают слишком много неприятных переживаний.

Q029 — `experiential\_avoidance` · `R` · `TRAIT`

Неприятное состояние не обязательно заставляет меня сразу менять свои действия.

Q030 — `experiential\_avoidance` · `D` · `TRAIT`

Иногда я меняю свои планы прежде всего ради того, чтобы не сталкиваться с внутренним дискомфортом.

Q031 — `intellectualization` · `D` · `TRAIT`

Когда меня что-то сильно задевает, я довольно быстро начинаю разбираться, почему это произошло и что это значит.

Q032 — `intellectualization` · `D` · `TRAIT`

В сложных переживаниях мне проще рассуждать о происходящем, чем говорить о том, что я непосредственно чувствую.

Q033 — `intellectualization` · `R` · `TRAIT`

Когда меня что-то эмоционально задевает, анализ обычно начинается не сразу — сначала я просто замечаю свою реакцию.

Q034 — `emotional\_suppression` · `D` · `TRAIT`

Я часто сдерживаю эмоции, чтобы они не были заметны другим.

Q035 — `emotional\_suppression` · `D` · `TRAIT`

Даже когда эмоция сильная, я обычно стараюсь не показывать её внешне.

Q036 — `emotional\_suppression` · `R` · `TRAIT`

Если меня что-то сильно задело, окружающие обычно могут заметить это по моей реакции.

Q037 — `polarized\_evaluation` · `D` · `TRAIT`

Если результат заметно хуже ожидаемого, мне легко воспринимать его как провал.

Q038 — `polarized\_evaluation` · `R` · `TRAIT`

Я обычно могу считать результат частично успешным, даже если он оказался далёк от идеального.

Q039 — `polarized\_evaluation` · `D` · `TRAIT`

Иногда один серьёзный недостаток заставляет меня обесценить всё остальное.

Q040 — `emotional\_awareness` · `D` · `TRAIT`

Мне обычно удаётся довольно точно понять, какую эмоцию я испытываю.

Q041 — `emotional\_awareness` · `D` · `TRAIT`

Даже при сильном переживании я обычно могу различить само чувство и желание немедленно что-то сделать под его влиянием.

Q042 — `emotional\_awareness` · `R` · `TRAIT`

Иногда моё состояние заметно меняется, но мне трудно понять, что именно меня так задело.

Q043 — `attachment\_anxiety` · `D` · `TRAIT`

Когда значимый человек отдаляется, я быстро начинаю беспокоиться о наших отношениях.

Q044 — `attachment\_anxiety` · `D` · `TRAIT`

Даже небольшое изменение в теплоте или доступности близкого человека может быстро привлечь моё внимание.

Q045 — `attachment\_anxiety` · `R` · `TRAIT`

Даже если близкий человек становится менее доступным, я обычно не сомневаюсь в устойчивости связи.

Q046 — `attachment\_anxiety` · `D` · `TRAIT`

Неясность в отношениях может занимать мои мысли сильнее, чем мне хотелось бы.

Q047 — `attachment\_avoidance` · `D` · `TRAIT`

Мне некомфортно чувствовать, что я слишком сильно нуждаюсь в другом человеке.

Q048 — `attachment\_avoidance` · `D` · `TRAIT`

Возможность сильно зависеть от близкого человека вызывает у меня внутреннее сопротивление.

Q049 — `attachment\_avoidance` · `R` · `TRAIT`

Мне легко опираться на близкого человека, когда я действительно в нём нуждаюсь.

Q050 — `attachment\_avoidance` · `D` · `TRAIT`

Даже в близких отношениях мне важно сохранять ощущение, что я способен обойтись без помощи другого человека.

Q051 — `interpersonal\_trust` · `D` · `TRAIT`

Пока человек не показал обратного, я обычно предполагаю, что в отношениях со мной у него нет скрытых недоброжелательных намерений.

Q052 — `interpersonal\_trust` · `D` · `TRAIT`

Если человек последовательно выполняет договорённости, моё доверие к нему обычно заметно растёт.

Q053 — `interpersonal\_trust` · `R` · `TRAIT`

Даже в достаточно близких отношениях мне бывает трудно полностью перестать искать признаки возможного подвоха.

Q054 — `boundary\_assertiveness` · `D` · `TRAIT`

Мне обычно удаётся отказаться от просьбы, если её выполнение существенно идёт против моих интересов.

Q055 — `boundary\_assertiveness` · `R` · `TRAIT`

Если значимый человек сильно недоволен моим решением, мне бывает трудно не изменить его только ради восстановления отношений.

Q056 — `boundary\_assertiveness` · `D` · `TRAIT`

Когда мои потребности сталкиваются с потребностями другого человека, я способен прямо обозначить свои.

Q057 — `autonomy\_value` · `D` · `TRAIT`

Если более выгодный вариант заметно ограничивает мою свободу выбора, это серьёзный аргумент против него.

Q058 — `autonomy\_value` · `D` · `TRAIT`

Я готов мириться с меньшим удобством, если взамен получаю больше возможности самостоятельно распоряжаться своей жизнью.

Q059 — `autonomy\_value` · `R` · `TRAIT`

Если условия жизни меня в целом устраивают, мне не особенно важно, насколько самостоятельно я могу определять их.

Q060 — `security\_value` · `D` · `TRAIT`

Между более предсказуемым вариантом и более перспективным, но рискованным, я нередко склоняюсь к первому.

Q061 — `security\_value` · `D` · `TRAIT`

Ради большей устойчивости я готов отказаться от части потенциальных возможностей.

Q062 — `security\_value` · `R` · `TRAIT`

Даже длительный период непредсказуемости сам по себе не делает вариант менее привлекательным для меня.

Q063 — `achievement\_value` · `D` · `TRAIT`

Я скорее выберу путь с возможностью серьёзного результата, чем более лёгкий путь без заметного роста.

Q064 — `achievement\_value` · `D` · `TRAIT`

Ощущение, что я становлюсь всё более компетентным в важном для меня деле, существенно влияет на удовлетворённость моей жизнью.

Q065 — `achievement\_value` · `R` · `TRAIT`

Если моя жизнь в целом приятна и наполнена, отсутствие заметных достижений меня не особенно беспокоит.

Q066 — `belonging\_value` · `D` · `TRAIT`

Даже очень успешная жизнь ощущалась бы для меня неполной без нескольких действительно близких отношений.

Q067 — `belonging\_value` · `D` · `TRAIT`

Мне важно чувствовать, что я принадлежу к кругу людей, где меня знают и принимают.

Q068 — `belonging\_value` · `R` · `TRAIT`

Для ощущения полноценной жизни мне не обязательно чувствовать себя частью близкого круга людей.

Q069 — `meaning\_value` · `D` · `TRAIT`

Мне важно чувствовать, что моя жизнь имеет смысл, а не просто состоит из задач.

Q070 — `meaning\_value` · `D` · `TRAIT`

Даже при внешне успешной жизни мне было бы трудно быть удовлетворённым, если бы я не видел в ней лично значимого направления.

Q071 — `meaning\_value` · `D` · `TRAIT`

Даже привлекательное занятие со временем теряет для меня ценность, если я перестаю понимать, зачем лично мне его продолжать.

Q072 — `growth\_value` · `D` · `TRAIT`

Личностное развитие для меня само по себе представляет ценность.

Q073 — `growth\_value` · `D` · `TRAIT`

Если выбранный путь долго не даёт мне ощущения внутреннего развития, это само по себе становится причиной задуматься о переменах.

Q074 — `growth\_value` · `D` · `TRAIT`

Возможность заметно расширить свои способности или понимание может быть для меня достаточной причиной выбрать более сложный путь.

Q075 — `agency` · `D` · `TRAIT`

Даже в сложной ситуации я ищу, на что именно могу повлиять.

Q076 — `agency` · `R` · `TRAIT`

Когда важная ситуация меня не устраивает, я иногда продолжаю ждать внешних изменений, хотя понимаю, что мог бы предпринять что-то сам.

Q077 — `agency` · `D` · `TRAIT`

Если я понимаю, что важная часть моей жизни меня больше не устраивает, я способен сам начать её менять, не дожидаясь внешнего толчка.

Q078 — `agency` · `D` · `TRAIT`

Даже когда я не могу изменить саму ситуацию, я обычно ищу, каким образом могу повлиять на собственный следующий шаг.

Q079 — `self\_efficacy` · `D` · `TRAIT`

Если задача для меня действительно важна, я обычно верю, что смогу найти способ с ней справиться.

Q080 — `self\_efficacy` · `R` · `TRAIT`

Столкнувшись с новой сложной задачей, я быстро начинаю сомневаться, что у меня получится.

Q081 — `self\_efficacy` · `D` · `TRAIT`

Даже без готового решения я обычно верю в свою способность разобраться по ходу дела.

Q082 — `external\_outcome\_attribution` · `D` · `TRAIT`

Когда важный результат не получается, я часто вижу основную причину в обстоятельствах, которые от меня не зависели.

Q083 — `external\_outcome\_attribution` · `D` · `TRAIT`

В важных результатах моей жизни удача и внешние обстоятельства, как мне кажется, играют очень большую роль.

Q084 — `external\_outcome\_attribution` · `R` · `TRAIT`

Когда что-то складывается хорошо, я обычно могу увидеть конкретные собственные решения, которые помогли этому произойти.

Q085 — `uncertainty\_tolerance` · `D` · `TRAIT`

Я способен действовать, даже когда не знаю наверняка, чем всё закончится.

Q086 — `uncertainty\_tolerance` · `D` · `TRAIT`

Отсутствие ясного ответа на важный вопрос может некоторое время оставаться нерешённым, не занимая всё моё внимание.

Q087 — `uncertainty\_tolerance` · `R` · `TRAIT`

Мне трудно начинать что-то важное, пока у меня нет достаточно ясного представления о возможном исходе.

Q088 — `uncertainty\_tolerance` · `D` · `TRAIT`

Если ситуация допускает несколько возможных объяснений, мне не обязательно сразу выбирать одно из них, чтобы чувствовать себя спокойно.

Q089 — `control\_need` · `D` · `TRAIT`

В важных ситуациях мне спокойнее, если ключевые решения и ход событий в значительной степени зависят от меня.

Q090 — `control\_need` · `D` · `TRAIT`

Если исход сильно зависит от других людей или случайности, мне становится заметно некомфортно.

Q091 — `control\_need` · `R` · `TRAIT`

Я спокойно отношусь к тому, что часть важных вещей невозможно контролировать.

Q092 — `decisiveness` · `D` · `TRAIT`

Получив достаточно информации, я обычно способен принять решение и двигаться дальше.

Q093 — `decisiveness` · `R` · `TRAIT`

Мне легко застрять между вариантами даже тогда, когда различия между ними уже понятны.

Q094 — `decisiveness` · `D` · `TRAIT`

Выбрав один из нескольких приемлемых вариантов, я обычно способен отказаться от попытки сохранить остальные возможности открытыми.

Q095 — `decision\_rumination` · `D` · `TRAIT`

После решения я могу снова и снова прокручивать, не стоило ли выбрать иначе.

Q096 — `decision\_rumination` · `D` · `TRAIT`

После важного выбора мне бывает трудно перестать искать признаки того, что решение могло быть ошибочным.

Q097 — `decision\_rumination` · `R` · `TRAIT`

Приняв решение, я обычно перестаю мысленно пересматривать его без новых оснований.

Q098 — `reassurance\_seeking` · `D` · `TRAIT`

Перед важным решением мне часто нужно услышать от другого человека, что я поступаю правильно.

Q099 — `reassurance\_seeking` · `D` · `TRAIT`

Если я тревожусь об отношениях, мне важно получить подтверждение, что всё в порядке.

Q100 — `reassurance\_seeking` · `R` · `TRAIT`

Даже когда я сомневаюсь, мне обычно не нужно чужое подтверждение, чтобы продолжить действовать согласно своему решению.

Q101 — `error\_intolerance` · `D` · `TRAIT`

Возможность ошибиться может заставить меня откладывать решение даже тогда, когда дальнейшее ожидание вряд ли даст новую информацию.

Q102 — `error\_intolerance` · `D` · `TRAIT`

После существенной ошибки мне бывает трудно просто скорректировать действия и двигаться дальше.

Q103 — `error\_intolerance` · `R` · `TRAIT`

Если решение необходимо принять, я способен выбрать вариант, даже понимая, что позже он может оказаться неправильным.

Q104 — `action\_initiation` · `D` · `TRAIT`

Когда решение уже принято, я обычно довольно быстро перехожу к первому конкретному действию.

Q105 — `action\_initiation` · `R` · `TRAIT`

Даже понимая, что именно нужно сделать, я могу долго откладывать первый шаг.

Q106 — `action\_initiation` · `D` · `TRAIT`

Если для начала действия мне не требуется дополнительная информация, мне обычно несложно просто начать.

Q107 — `adaptive\_flexibility` · `D` · `TRAIT`

Если выбранный способ долго не даёт результата, я способен отказаться от него и попробовать принципиально другой.

Q108 — `adaptive\_flexibility` · `R` · `TRAIT`

Даже когда выбранная стратегия явно работает плохо, мне бывает трудно перестать вкладываться именно в неё.

Q109 — `adaptive\_flexibility` · `D` · `TRAIT`

Новая информация может заметно изменить мой план, даже если я уже много вложил в первоначальный вариант.

Q110 — `fear\_of\_evaluation` · `D` · `TRAIT`

Возможность негативной оценки может заставить меня выражать себя осторожнее, чем мне хотелось бы.

Q111 — `fear\_of\_evaluation` · `D` · `TRAIT`

Перед публичным проявлением я часто думаю о том, как меня оценят.

Q112 — `fear\_of\_evaluation` · `R` · `TRAIT`

Я способен показать результат своей работы или высказать позицию ещё до того, как уверен, что окружающие отреагируют положительно.

Q113 — `fear\_of\_evaluation` · `D` · `TRAIT`

Иногда я отказываюсь от заметного действия не потому, что сам считаю его неправильным, а потому, что представляю возможную реакцию окружающих.

Q114 — `authentic\_expression` · `D` · `TRAIT`

То, как я выражаю свои взгляды другим людям, обычно довольно точно соответствует тому, что я действительно думаю.

Q115 — `authentic\_expression` · `D` · `TRAIT`

В общении мне обычно не приходится заметно менять свои предпочтения или манеру самовыражения, чтобы соответствовать окружению.

Q116 — `authentic\_expression` · `R` · `TRAIT`

Если моё настоящее мнение отличается от мнения окружающих, я иногда выражаю более удобную для ситуации версию своей позиции.

Q117 — `authentic\_expression` · `D` · `TRAIT`

Мне обычно несложно открыто признавать собственные предпочтения, даже если они отличаются от привычных для моего окружения.

Q118 — `visibility\_desire` · `D` · `TRAIT`

Мне хочется, чтобы мои идеи, работа или личность были заметны большему количеству людей.

Q119 — `visibility\_desire` · `D` · `TRAIT`

Возможность доносить свои идеи или результаты до большой аудитории кажется мне привлекательной.

Q120 — `visibility\_desire` · `R` · `TRAIT`

Даже если мне есть что показать или сказать, расширение собственной публичной заметности само по себе меня мало привлекает.

Q121 — `inner\_critic` · `D` · `TRAIT`

Когда я ошибаюсь, мой внутренний разговор с собой часто становится жёстким.

Q122 — `inner\_critic` · `D` · `TRAIT`

Если мой результат заметно хуже ожидаемого, я склонен критиковать себя сильнее, чем просто анализировать ошибку.

Q123 — `inner\_critic` · `R` · `TRAIT`

После неудачи мне обычно удаётся разговаривать с собой скорее конструктивно, чем обвиняюще.

Q124 — `vulnerability\_avoidance` · `D` · `TRAIT`

Мне трудно показывать значимым людям, что я действительно нуждаюсь в их поддержке.

Q125 — `vulnerability\_avoidance` · `D` · `TRAIT`

Даже когда мне тяжело, мне часто проще выглядеть справляющимся, чем показать свою растерянность или слабость.

Q126 — `vulnerability\_avoidance` · `R` · `TRAIT`

Я способен сказать близкому человеку, что мне страшно, больно или трудно, не пытаясь сразу выглядеть сильнее, чем чувствую себя на самом деле.

Q127 — `performance\_based\_self\_worth` · `D` · `TRAIT`

Когда у меня долго нет значимых результатов, моё отношение к себе становится хуже.

Q128 — `performance\_based\_self\_worth` · `D` · `TRAIT`

Серьёзная неудача может заставить меня сомневаться не только в своих действиях, но и в собственной ценности.

Q129 — `performance\_based\_self\_worth` · `R` · `TRAIT`

Неудачный результат обычно не заставляет меня чувствовать себя менее ценным человеком.

Q130 — `performance\_based\_self\_worth` · `D` · `TRAIT`

Ощущение собственной ценности у меня заметно связано с тем, насколько компетентным и успешным я себя чувствую.

Q131 — `stable\_self\_worth` · `D` · `TRAIT`

Даже в периоды, когда у меня мало поводов собой гордиться, базовое уважение к себе обычно сохраняется.

Q132 — `stable\_self\_worth` · `D` · `TRAIT`

Я могу видеть в себе серьёзные недостатки и при этом не воспринимать себя целиком как «плохого» или менее достойного человека.

Q133 — `stable\_self\_worth` · `R` · `TRAIT`

Моё общее отношение к себе может заметно меняться вслед за периодами успехов и неудач.

Q134 — `achievement\_drive` · `D` · `TRAIT`

Достигнув важной цели, я довольно быстро начинаю думать о следующем уровне.

Q135 — `achievement\_drive` · `D` · `TRAIT`

Возможность превзойти свой прежний результат сама по себе способна сильно меня мотивировать.

Q136 — `achievement\_drive` · `R` · `TRAIT`

Если текущий уровень жизни меня устраивает, у меня обычно нет сильной потребности постоянно повышать планку.

Q137 — `need\_awareness` · `D` · `TRAIT`

Когда моё состояние ухудшается, мне обычно удаётся понять, чего именно мне сейчас не хватает.

Q138 — `need\_awareness` · `D` · `TRAIT`

Я обычно могу отличить собственное желание от того, чего от меня ожидают окружающие.

Q139 — `need\_awareness` · `R` · `TRAIT`

Я могу долго чувствовать, что меня что-то не устраивает, не понимая, чего именно мне хотелось бы вместо этого.

Q140 — `money\_security` · `D` · `TRAIT`

Наличие финансового запаса заметно влияет на моё ощущение безопасности.

Q141 — `money\_security` · `D` · `TRAIT`

Финансовая неопределённость способна сильно снижать моё чувство внутренней устойчивости.

Q142 — `money\_security` · `R` · `TRAIT`

Даже при нестабильном доходе мне обычно удаётся сохранять ощущение базовой безопасности.

Q143 — `money\_autonomy` · `D` · `TRAIT`

Деньги важны для меня прежде всего потому, что расширяют свободу выбора.

Q144 — `money\_autonomy` · `D` · `TRAIT`

Возможность финансово не зависеть от решений других людей для меня особенно важна.

Q145 — `money\_autonomy` · `R` · `TRAIT`

Моё ощущение свободы относительно мало зависит от того, сколько финансовых ресурсов у меня есть.

Q146 — `money\_status\_achievement` · `D` · `TRAIT`

Уровень моего дохода в некоторой степени служит для меня показателем того, насколько успешно я реализуюсь.

Q147 — `money\_status\_achievement` · `D` · `TRAIT`

Финансовый результат делает для меня профессиональные или личные достижения более ощутимыми.

Q148 — `money\_status\_achievement` · `R` · `TRAIT`

Я легко могу считать себя очень успешным человеком, даже если это почти никак не отражается на моём финансовом положении.

Q149 — `anxiety\_state` · `D` · `STATE`

За последние 14 дней я часто чувствовал внутреннее напряжение или тревогу.

Q150 — `anxiety\_state` · `D` · `STATE`

За последние 14 дней мне бывало трудно остановить или контролировать беспокойство.

Q151 — `anxiety\_state` · `D` · `STATE`

За последние 14 дней я часто ожидал, что может произойти что-то неприятное.

Q152 — `low\_mood\_state` · `D` · `STATE`

За последние 14 дней я часто чувствовал подавленность или эмоциональный спад.

Q153 — `low\_mood\_state` · `D` · `STATE`

За последние 14 дней мне было заметно сложнее испытывать интерес или удовольствие от вещей, которые обычно меня вовлекают.

Q154 — `low\_mood\_state` · `D` · `STATE`

За последние 14 дней мне часто не хватало энергии даже для обычных дел.

Q155 — `relational\_uncertainty` · `D` · `CONTEXT`

Неопределённость в близких отношениях переносится мной тяжелее, чем неопределённость в большинстве других областей жизни.

Q156 — `support\_type` · `D` · `CONTEXT`

Мне легче попросить помощи в практическом вопросе, чем признаться другому человеку, что эмоционально мне тяжело.

Q157 — `evaluation\_source` · `D` · `CONTEXT`

Негативная оценка значимого для меня человека обычно задевает меня сильнее, чем мнение незнакомой аудитории.

Q158 — `stakes\_sensitive\_control` · `D` · `CONTEXT`

Чем значимее для меня возможные последствия решения, тем сильнее мне хочется контролировать происходящее.

Q159 — `financial\_baseline\_security` · `D` · `MODERATOR`

Насколько сейчас ваши основные финансовые потребности закрыты?

Q160 — `current\_meaning` · `D` · `MODERATOR`

Насколько сейчас вы ощущаете, что ваша жизнь имеет понятное вам направление и смысл?

APPENDIX B. CANONICAL VFC BANK V1.0

UI: left/right randomize per session; сохранять `selected\_value`, а не A/B.

VFC01 — `autonomy` vs `security`

Option 1: A: иметь больше свободы самостоятельно определять свою жизнь, даже ценой меньшей предсказуемости.

Option 2: B: иметь больше устойчивости и предсказуемости, даже ценой части свободы выбора.

VFC02 — `achievement` vs `autonomy`

Option 1: A: получить возможность добиться значительно большего результата.

Option 2: B: сохранить больше свободы распоряжаться собой и своим временем.

VFC03 — `autonomy` vs `belonging`

Option 1: A: иметь возможность жить преимущественно на собственных условиях.

Option 2: B: сохранять тесную связь и чувство принадлежности к важным людям.

VFC04 — `meaning` vs `autonomy`

Option 1: A: заниматься тем, что ощущается глубоко осмысленным.

Option 2: B: иметь максимальную свободу самостоятельно выбирать направление жизни.

VFC05 — `autonomy` vs `growth`

Option 1: A: сохранить свободу выбирать собственный путь.

Option 2: B: выбрать путь, который сильнее развивает меня, даже если он ограничивает часть свободы.

VFC06 — `security` vs `achievement`

Option 1: A: сохранить надёжный и устойчивый уровень жизни.

Option 2: B: рискнуть частью устойчивости ради возможности добиться значительно большего.

VFC07 — `belonging` vs `security`

Option 1: A: сохранить близость и принадлежность к важным людям.

Option 2: B: выбрать более устойчивый и безопасный для себя вариант.

VFC08 — `security` vs `meaning`

Option 1: A: сохранить предсказуемость и устойчивость жизни.

Option 2: B: выбрать менее предсказуемый путь, который ощущается значительно более осмысленным.

VFC09 — `growth` vs `security`

Option 1: A: выбрать путь, который сильнее меня развивает.

Option 2: B: сохранить больше устойчивости и предсказуемости.

VFC10 — `achievement` vs `belonging`

Option 1: A: использовать возможность значительного достижения, даже если отношениям временно достанется меньше моего времени.

Option 2: B: сохранить больше времени и включённости в важные отношения, даже ценой части возможностей.

VFC11 — `meaning` vs `achievement`

Option 1: A: заниматься более осмысленным для себя делом, даже если результат будет скромнее.

Option 2: B: выбрать возможность значительно большего результата, даже если сама деятельность ощущается менее значимой.

VFC12 — `achievement` vs `growth`

Option 1: A: получить более заметный внешний результат.

Option 2: B: получить опыт, который сильнее меня развивает, даже если внешний результат будет скромнее.

VFC13 — `belonging` vs `meaning`

Option 1: A: сохранить тесную связь с важными людьми.

Option 2: B: следовать лично значимому направлению, даже если это создаст большую дистанцию.

VFC14 — `growth` vs `belonging`

Option 1: A: выбрать опыт, который существенно меня развивает.

Option 2: B: сохранить привычную близость и включённость в отношения.

VFC15 — `meaning` vs `growth`

Option 1: A: выбрать путь, который ощущается более осмысленным уже сейчас.

Option 2: B: выбрать путь, который сильнее меня изменит и разовьёт.

APPENDIX C. CANONICAL DISPLAY ORDER SOURCE

Trait order

Q001, Q007, Q004, Q057, Q003, Q009, Q064, Q005, Q072, Q011, Q079, Q066, Q017, Q043, Q002, Q082, Q006, Q110, Q008, Q024, Q010, Q127, Q138, Q051, Q137, Q085, Q117, Q134, Q012, Q040, Q089, Q114, Q060, Q021, Q098, Q140, Q139, Q013, Q047, Q075, Q121, Q069, Q031, Q092, Q143, Q054, Q118, Q027, Q102, Q131, Q073, Q034, Q081, Q018, Q044, Q083, Q111, Q025, Q128, Q052, Q086, Q135, Q041, Q090, Q115, Q061, Q022, Q099, Q141, Q014, Q048, Q076, Q122, Q070, Q032, Q093, Q144, Q055, Q119, Q028, Q103, Q132, Q074, Q035, Q080, Q019, Q045, Q084, Q112, Q026, Q129, Q053, Q087, Q136, Q042, Q091, Q116, Q062, Q023, Q100, Q142, Q015, Q049, Q077, Q123, Q071, Q033, Q094, Q145, Q056, Q120, Q029, Q101, Q133, Q037, Q036, Q088, Q020, Q046, Q107, Q113, Q038, Q130, Q058, Q095, Q146, Q104, Q030, Q108, Q063, Q096, Q109, Q039, Q016, Q050, Q078, Q124, Q059, Q097, Q147, Q105, Q065, Q125, Q068, Q106, Q148, Q126, Q067

V1.3 DEEP использует этот order как source, но фильтрует answered\_master\_ids из CORE/adaptive.

State/context order

Q149, Q152, Q150, Q153, Q151, Q154, Q155, Q157, Q156, Q158, Q159, Q160

VFC order

VFC08, VFC02, VFC13, VFC06, VFC15, VFC03, VFC12, VFC07, VFC04, VFC10, VFC01, VFC14, VFC11, VFC05, VFC09

APPENDIX D. RECOMMENDED IMPLEMENTATION ORDER

Repo/CI/config loader/versioning.

DB/users/sessions/consent.

Telegram skeleton.

Question rendering + autosave/resume.

CORE 24.

CORE signals/confidence/conflicts/resources.

Adaptive engine.

CORE fixtures.

FREE report + validation.

Personalized paywall.

Payment/webhook/entitlement.

DEEP queue excluding answered CORE IDs.

State/context/VFC.

Full scoring 46 scales.

Response quality.

37 patterns / 12 conflicts / suppression.

Full synthesis cycles/resources.

CORE→DEEP revision.

Personal rule candidates.

FULL structured LLM generation.

PDF.

Admin/analytics/pilot export.

Security/monitoring/backups.

Golden profiles + E2E staging.

Production release + handoff.

APPENDIX E. FINAL NON-NEGOTIABLES

CORE бесплатный и короткий: 24–30.

DEEP только после entitlement.

CORE answers входят в FULL и не задаются повторно.

46 primary scales считаются только при полном наборе items.

LLM не считает психологию.

Counter-evidence обязателен.

State ≠ trait.

Value tension ≠ conflict автоматически.

Low visibility ≠ fear автоматически.

Autonomy ≠ defensive independence автоматически.

Money safety ≠ pathology при реальной финансовой нестабильности.

Нет clinical diagnosis.

Нет population percentiles до norms.

Payment access только после verified webhook.

Entitlement переживает AI/PDF failures.

FREE никогда не содержит FULL payload.

PDF строится из того же validated FULL JSON.

Analysis snapshot immutable/versioned.

Psych logic — backend/config, не handlers.

Главный продукт — синтез, а не 46 цифр.

FINAL DEVELOPER DIRECTIVE

Построй production-ready Telegram-систему «Инструкция к себе» V1.3 как двухступенчатый assessment-продукт. Короткий бесплатный CORE из 24 обязательных и 0–6 адаптивных вопросов должен детерминированно вычислять CORE signals, confidence, conflicts и resources, генерировать валидируемый FREE report и персонализированный paywall. После подтверждённой server-side оплаты пользователь получает DEEP-доступ, продолжает тот же master assessment без повторения уже отвеченных items, завершает master trait/state/context и VFC, после чего backend рассчитывает 46 primary scales, state/context/quality, patterns/conflicts/suppression/resources, строит 3–5 системных циклов, сравнивает CORE-гипотезу с FULL evidence, формирует 10 персональных правил и только затем передаёт structured package LLM для персонализированного русскоязычного отчёта. FULL должен быть доступен в Telegram и PDF. Платежи и jobs должны быть idempotent, психологические вычисления — versioned/reproducible, продукт — безопасен, наблюдаем, тестируем и готов к пилотной психометрической калибровке.

Не считать задачу выполненной, если создан просто Telegram quiz. Задача выполнена только тогда, когда существует end-to-end система:

короткое узнавание → доверие → естественный paid deepening → полная структурированная карта → системный синтез → персональная инструкция → измеримая воронка → данные для психометрической калибровки.



