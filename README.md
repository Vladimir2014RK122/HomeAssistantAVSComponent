# Home Assistant custom component for AVS-control controllers 

uses avs-bus multicast transport

## How to install custom component:

1. open path: `<config directory>/custom_components`
2. copy folder `avs` to directory `<config directory>/custom_components/`
3. setup `configuration.yaml`

### setup `configuration.yaml`:

First what you have to do is create platform:

	avs:
		mcast_group: '239.1.1.11'
		ha_avs_address: '12345'
		
**Required parameters:**
    	
> **mcast\_group** : *string*<br>
> multicast group which uses by avs-bus protocol<br>
> *range:* only 239.1.1.11<br>
> *example:* `mcast\_group: '239.1.1.11'`

> **ha\_avs\_address** : *string*<br>
> address avs-bus device. Home assistant address into avs-bus network<br>
> *range:* 1...65534<br>
> *example:* `ha\_avs\_address: '12345'`



After previos step (setup platform) you can add entities:

### Light
	
	light:
	  - platform: avs
	    name: Living sconce
	    address: '12'
	    state_address: '19'
	    
**Required parameters:**

> **address** : *string*<br>
> address for discrete control device - on/off<br>
> *avs-bus type:* type-1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `address: '12345'`

<br>
**Optional parameters:**

> **name** : *string*<br>
> entity name<br>
> *example:* `name: Living sconce`

> **state\_address** : *string*<br>
> on/off status<br>
> *avs-bus type:* type-1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `state_address: '19'`



Next pair of parameters unlock color picker, but parameters have to use together:

> **color\_address** : *string*<br>
> color address<br>
> *avs-bus type:* type-7 (3 byte)<br>
> *range:* 0x0...0xFFFFFF<br>
> *example:* `color_address: '10'`

> **color\_state\_address** : *string*<br>
> color status address<br>
> *avs-bus type:* type-7 (3 byte)<br>
> *range:* 0x0...0xFFFFFF<br>
> *example:* `color_state_address: '18'`


Next pair of parameters unlock white channel controls, but parameters have to use together:

> **white\_address** : *string*<br>
> white channel address<br>
> *avs-bus type:* type-2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `white_address: '7'`

> **white\_state\_address:** : *string*<br>
> white channel status address<br>
> *avs-bus type:* type-2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `white_state_address: '16'`

Next pair of parameters unlock color temperature controls, but parameters have to use together:

> **color\_temperature\_address** : *string*<br>
> color temperature address<br>
> *avs-bus type:* type-2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `color_temperature_address: '25'`

> **color\_temperature\_state\_address** : *string*<br>
> color temperature status address <br>
> *avs-bus type:* type-2 (1 byte)<br>
> *range:* 0...255<br>
> *example:* `color_temperature_state_address: '111'`


### Climate

	climate:
	  - platform: avs
	    name: TemperatureIn Kitchen
	    on_off: '3'
	    on_off_status: '8'
	    measured_temperature_status: '5'
	    setpoint_temperature: '2'
	    setpoint_temperature_status: '7'
	    operation_mode: '1'
	    operation_mode_status: '6'
	    heat_value_status: '11'
	    cool_value_status: '12'
	    heat_cool_status: '13'
	    error_status: '14'
	    setpoint_step: 1.0    
	    setpoint_max_temp: 50.0
	    setpoint_min_temp: 7.0
	    use_humidity: True
	    use_aux_heat: True
	    measured_humidity_status: '2'
	    setpoint_humidity: '7'
	    setpoint_humidity_status: '2'
	    aux_heat: '3'
	    aux_heat_status: '8'
	    poll : True
	    scan_interval: 30

**Required parameters:**

> **measured\_temperature_status** : *string*<br>
> address measured temperature<br>
> *avs-bus type:* type-6 (4 byte)<br>
> *range:* -100.0 ... 100.0<br>
> *example:* `measured_temperature_status: '5'`    

> **setpoint\_temperature** : *string*<br>
> address for setting target temperature<br>
> *avs-bus type:* type-6 (4 byte)<br>
> *range:* -100.0 ... 100.0<br>
> *example:* `setpoint_temperature: '2'`    

> **setpoint\_temperature\_status** : *string*<br>
> address for getting target temperature<br>
> *avs-bus type:* type-6 (4 byte)<br>
> *range:* -100.0 ... 100.0<br>
> *example:* `setpoint_temperature_status: '7'` 

<br>
**Optional parameters:**

> **name** : *string*<br>
> entity name<br>
> *example:* `name: Living sconce`

> **on\_off** : *string*<br>
> on/off thermostat<br>
> *avs-bus type:* type-1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `on_off: '3'`	 

> **on\_off\_status** : *string*<br>
> thermostat on-off status<br>
> *avs-bus type:* type-1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `on_off_status: '8'`	 

> **operation\_mode** : *string*<br>
> set operation mode<br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0/1/2<br>
> *example:* `operation_mode: '1'`	  

> **operation\_mode\_status** : *string*<br>
> get operation mode status <br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0/1/2<br>
> *example:* `operation_mode_status: '6'`  

> **heat\_value\_status** : *string*<br>
> show heating status <br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0...255<br>
> *example:* `heat_value_status: '11'`  

> **cool\_value\_status** : *string*<br>
> show cooling status <br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0...255<br>
> *example:* `cool_value_status: '12'`  

> **heat\_cool\_status** : *string*<br>
> show instance heat or cool status. 0 - all off, 1 - heating, 2 - cooling<br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0/1/2<br>
> *example:* `heat_cool_status: '13'` 

> **error\_status** : *string*<br>
> showing thermostat got to error state(usialy for 1-wire sensor)<br>
> *avs-bus type:* type-1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `error_status: '14'`

> **setpoint\_step** : *string*<br>
> step for changing target temperature<br>
> *type:* float<br>
> *range:* 0.0...2.0<br>
> *example:* `setpoint_step: 1.0`

> **setpoint\_max\_temp** : *float*<br>
> max target temperature<br>
> *range:* -100.0...100.0<br>
> *example:* `setpoint_max_temp: 50.0`

> **setpoint\_min\_temp** : *float*<br>
> min target temperature<br>
> *range:* -100.0...100.0<br>
> *example:* `setpoint_min_temp: 7.0`


Next three parameters unlock humidity controls, but parameters have to use together:


> **use\_humidity** : *boolean*<br>
> True value unlock humidity controls<br>
> *range:* True/False<br>
> *example:* `use_humidity: True`

> **measured\_humidity\_status** : *string*<br>
> measured humidity <br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0...100<br>
> *example:* `measured_humidity_status: '2'`

> **setpoint\_humidity** : *string*<br>
> setting target humidity <br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0...100<br>
> *example:* `setpoint_humidity: '7'`

> **setpoint\_humidity\_status** : *string*<br>
> getting target humidity status <br>
> *avs-bus type:* type-2 (2 byte)<br>
> *range:* 0...100<br>
> *example:* `setpoint_humidity: '7'`

Next three parameters unlock auxiliary heat controls, but parameters have to use together:

> **use\_aux\_heat** : *boolean*<br>
> True value unlock auxiliary heat controls<br>
> *range:* True/False<br>
> *example:* `use_aux_heat: True`

> **aux\_heat** : *string*<br>
> on/off aux heat control <br>
> *avs-bus type:* type-1 (2 bit)<br>
> *range:* 0/1<br>
> *example:* `aux_heat: '3'`

> **aux\_heat\_status** : *string*<br>
> on/off aux heat status <br>
> *avs-bus type:* type-1 (1 bit)<br>
> *range:* 0/1<br>
> *example:* `aux_heat_status: '8'`


> **poll** : *boolan*<br>
> poll statuses <br>
> *range:* True/False<br>
> *example:* `poll : True`

> **scan\_interval** : *integer*<br>
> poll period in seconds <br>
> *range:* 10...3600<br>
> *example:* `scan_interval: 30`
	    



### Sensor

	sensor:
	  - platform: avs
	    name: 'living sensor Temp'
	    state_address: '64'
	    type: 'temperature'
	    units: "˚C"
	    

**Required parameters:**

> **state\_address** : *string*<br>
> getting data<br>
> *example:* `state_address: '64'`  

> **type** : *string*<br>
> type of data<br>
> *example:* `type: 'temperature'` 

> **units** : *string*<br>
> units of data<br>
> *example:* `units: "˚C"` 


<br>

**Optional parameters:**

> **name** : *string*<br>
> entity name<br>
> *example:* `name: Living sconce`

