# Home Assistant custom component для контроллеров AVS-control 

Используется avs-bus multicast транспорт

## Как установить custom component:

1. откройте директорию: `<config directory>/custom_components`
2. скопируйте папку `avs` в директорию `<config directory>/custom_components/`
3. настройте `configuration.yaml`

### Настройка `configuration.yaml`:

В первую очередь нужно добавить платформу:

	avs:
		mcast_group: '239.1.1.11'
		ha_avs_address: '12345'
		
**Наобходимые параметры:**
    	
> **mcast\_group** : *string*<br>
> multicast группа, которая используется протоколом avs-bus<br>
> *диапазон:* только 239.1.1.11<br>
> *пример:* `mcast_group: '239.1.1.11'`

> **ha\_avs\_address** : *string*<br>
> address avs-bus device. Home assistant address into avs-bus network<br>
> *range:* 1...65534<br>
> *example:* `ha_avs_address: '12345'`



После установки платформы можно добавить сущности (entity):

### Button

	button:
		- platform: avs
		  name: 'button 1'
		  address: '12'
		  dpt: 2
		  data: '125'

**Обязательные параметры:**

> **address** : *string*<br>
> адрес, используемый для отправки команд<br>
> *range:* AVS-DPT1...AVS-DPT11<br>
> *example:* `address: '12345'`

> **dpt** : *uint*<br>
> тип данных<br>
> *range:* AVS-DPT1...AVS-DPT11 (1...11)<br>
> *example:* `dpt: 2`

> **data** : *string*<br>
> значение, которое будет отправлятся при нажатии кнопки<br>
> *range:* значение должно соответствовать установленному типу данных<br>
> *example:* `data: '125'`

**Опциональные параметры:**

> **name** : *string*<br>
> Имя сущности<br>
> *example:* `name:  'кнопка`

### Light
	
	light:
	  - platform: avs
	    name: Living sconce
	    address: '12'
	    state_address: '19'
		brightness_address: '13'
		brightness_state_address: '20'
	    
**Обязательные параметры:**

> **address** : *string*<br>
> адрес для дискретного управления - вкл/выкл<br>
> *avs-bus type:* AVS-DPT1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `address: '123'`

<br>

**Опциональные параметры:**

> **name** : *string*<br>
> Имя сущности<br>
> *example:* `name: Living sconce`

> **state\_address** : *string*<br>
> адрес статуса состояния вкл/выкл<br>
> *avs-bus type:* AVS-DPT1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `state_address: '19'`

> **brightness\_address** : *string*<br>
> адрес управления яркостью<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `brightness_address: '19'`

> **brightness\_state\_address** : *string*<br>
> адрес статуса яркости<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `brightness_state_address: '19'`


Следующая пара паремтров посзволяет управлять цветом:

> **color\_address** : *string*<br>
> адрес управления цветом<br>
> *avs-bus type:* AVS-DPT7 (3 byte)<br>
> *range:* 0x0...0xFFFFFF<br>
> *example:* `color_address: '10'`

> **color\_state\_address** : *string*<br>
> адрес статуса цвета<br>
> *avs-bus type:* AVS-DPT7 (3 byte)<br>
> *range:* 0x0...0xFFFFFF<br>
> *example:* `color_state_address: '18'`

> **hue\_address** : *string*<br>
> адрес HUE<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `hue_address: '18'`

> **hue\_state\_address** : *string*<br>
> адрес статуса HUE<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `hue_state_address: '18'`

> **saturation\_address** : *string*<br>
> адрес SATURATION<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `saturation_address: '18'`

> **saturation\_state\_address** : *string*<br>
> адрес статуса SATURATION<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `saturation_state_address: '18'`

Следующая пара пареметров посзволяет управлять световой температурой:

> **color\_temperature\_address** : *string*<br>
> адрес управления световой температурой<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `color_temperature_address: '25'`

> **color\_temperature\_state\_address** : *string*<br>
> адрес статуса световой температуры <br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `color_temperature_state_address: '111'`



Следующая пара пареметров посзволяет управлять отдельным каналом белой ленты:

> **white\_address** : *string*<br>
> адрес яркости белого канала<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `white_address: '7'`

> **white\_state\_address:** : *string*<br>
> статус яркости белого канала<br>
> *avs-bus type:* AVS-DPT2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `white_state_address: '16'`


### Climate

	climate:
	  - platform: avs
	    name: Climate Kitchen
		thermostat_mode: 'heat_and_cool'
	    on_off: '3'
	    on_off_status: '8'
	    measured_temperature_status: '5'
	    setpoint_temperature: '2'
	    setpoint_temperature_status: '7'
	    operation_mode: '1'
	    operation_mode_status: '6'
	    heat_cool_status: '13'
	    setpoint_step: 1.0    


**Обязательные параметры:**

> **measured\_temperature_status** : *string*<br>
> адрес измеренной температуры<br>
> *avs-bus type:* AVS-DPT6 (float)<br>
> *range:* -100.0 ... 100.0<br>
> *example:* `measured_temperature_status: '5'`    

> **setpoint\_temperature** : *string*<br>
> адрес задания уставки<br>
> *avs-bus type:* AVS-DPT6 (float)<br>
> *range:* -100.0 ... 100.0<br>
> *example:* `setpoint_temperature: '2'`    

> **setpoint\_temperature\_status** : *string*<br>
> адрес статуса заданной уставки<br>
> *avs-bus type:* AVS-DPT6 (4 byte)<br>
> *range:* -100.0 ... 100.0<br>
> *example:* `setpoint_temperature_status: '7'` 

> **heat\_cool\_status** : *string*<br>
> адрес статуса состояния регулятора, 0 - all off, 1 - heating, 2 - cooling<br>
> *avs-bus type:* AVS-DPT2 (2 byte)<br>
> *range:* 0/1/2<br>
> *example:* `heat_cool_status: '13'` 


<br>

**Опциональные параметры:**

> **name** : *string*<br>
> имя сущности<br>
> *example:* `name: Living sconce`

> **thermostat\_mode** : *string*<br>
> режим работы термостата<br>
> *range:* heat/cool/heat_and_cool<br>
> *example:* `thermostat_mode: 'heat_cool'`  

> **on\_off** : *string*<br>
> адрес управления термостатом вкл/выкл<br>
> *avs-bus type:* AVS-DPT1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `on_off: '3'`	 

> **on\_off\_status** : *string*<br>
> адрес статуса состояния вкл/выкл термостата<br>
> *avs-bus type:* AVS-DPT1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `on_off_status: '8'`	 

> **operation\_mode** : *string*<br>
> адрес выбора сохраненных уставок<br>
> *avs-bus type:* AVS-DPT2 (2 byte)<br>
> *range:* 0/1/2<br>
> *example:* `operation_mode: '1'`	  

> **operation\_mode\_status** : *string*<br>
> адрес статуса выбранной уставки из созраненных<br>
> *avs-bus type:* AVS-DPT2 (2 byte)<br>
> *range:* 0/1/2<br>
> *example:* `operation_mode_status: '6'`  

> **setpoint\_step** : *string*<br>
> шаг изменения уставки<br>
> *type:* float<br>
> *range:* 0.0...2.0<br>
> *example:* `setpoint_step: 1.0`

> **setpoint\_max\_temp** : *float*<br>
> максимальное значение уставки<br>
> *range:* -100.0...100.0<br>
> *example:* `setpoint_max_temp: 50.0`

> **setpoint\_min\_temp** : *float*<br>
> минимальное значения уставки<br>
> *range:* -100.0...100.0<br>
> *example:* `setpoint_min_temp: 7.0`

> **poll** : *boolan*<br>
> отправлять перриодически запросы состояния <br>
> *range:* True/False<br>
> *example:* `poll : False`

> **scan\_interval** : *integer*<br>
> период запросов состояний, в секундах <br>
> *range:* 10...3600<br>
> *example:* `scan_interval: 30`
	    



### Sensor

	sensor:
	  - platform: avs
	    name: 'living sensor Temp'
	    state_address: '64'
		dpt: '6'
	    type: 'temperature'
	    units: "˚C"
	    

**Обязательные параметры:**

> **state\_address** : *string*<br>
> адрес статуса данных<br>
> *example:* `state_address: '64'`  

> **dpt** : *uint*<br>
> тип данных<br>
> *range:* AVS-DPT1...AVS-DPT11 (1...11)<br>
> *example:* `dpt: 2`

<br>

**Опциональные параметры:**

> **name** : *string*<br>
> имя сущности<br>
> *example:* `name: Температура на улице`

> **type** : *string*<br>
> тип даннных для отобраения<br>
> *example:* `type: 'temperature'` 

> **units** : *string*<br>
> единицы измерения<br>
> *example:* `units: "˚C"` 


### Switch

	switch:
	  - platform: avs
    	name: switch_2
    	address: '54'
    	state_address: '55'
    	dpt: 2
    	data_0: '150'
    	data_1: '240'

**Обязательные параметры:**

> **address** : *string*<br>
> адрес отправки значения<br>
> *example:* `address: '64'` 

> **state\_address** : *string*<br>
> адрес статуса данных<br>
> *example:* `state_address: '64'`  

> **dpt** : *uint*<br>
> тип данных<br>
> *range:* AVS-DPT1...AVS-DPT11 (1...11)<br>
> *example:* `dpt: 2`

> **data\_0** : *string*<br>
> первое значение, в зависимости от выбранного типа данных<br>
> *example:* `data_0: '0'` 

> **data\_1** : *string*<br>
> второе значение, в зависимости от выбранного типа данных<br>
> *example:* `data_1: '200'` 

<br>

**Опциональные параметы:**

> **name** : *string*<br>
> имя сущности<br>
> *example:* `name: Люстра в гостиной`