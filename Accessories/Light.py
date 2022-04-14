from pyhap.const import CATEGORY_TELEVISION
from Accessories.Light_request import API
from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_LIGHTBULB
import logging

logger = logging.getLogger(__name__)

class NeoPixelLightStrip(Accessory):

    category = CATEGORY_LIGHTBULB
    NAME = 'Effects'

    def __init__(self, base_url,json_config, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.set_info_service(
            manufacturer='Max',
            model='SmartLight',
            firmware_revision='1.0',
            serial_number='1235678'
        )

        
        serv_light = self.add_preload_service(
            'Lightbulb', chars=['On', 'Hue', 'Saturation', 'Brightness'])

        # Configure our callbacks
        self.char_hue = serv_light.configure_char(
            'Hue', setter_callback=self.set_hue)
        self.char_saturation = serv_light.configure_char(
            'Saturation', setter_callback=self.set_saturation)
        self.char_on = serv_light.configure_char(
            'On', setter_callback=self.set_state)
        self.char_bri = serv_light.configure_char(
            'Brightness', setter_callback=self.set_brightness)


        # Set variables
        self.accessory_state = 0 
        self.hue = 0  
        self.saturation = 100  
        self.brightness = 100  
        self.api = API(base_url,json_config)
        self.char_hue.value = self.hue
        self.char_bri.value = self.brightness
        self.char_saturation.value = self.saturation
        self.char_on.value = self.accessory_state
        self.char_hue.notify()
        self.char_bri.notify()
        self.char_saturation.notify()
        self.char_on.notify()

        
        self._active = 0
        self._effect = 1
        self.SOURCES = {}
        for e,__ in self.api.effects.items():
            self.SOURCES[e] = 0


        tv_service = self.add_preload_service(
            'Television', ['Name',
                           'ConfiguredName',
                           'Active',
                           'ActiveIdentifier',
                           'SleepDiscoveryMode'],
        )
        self._active = tv_service.configure_char(
            'Active', value=0,
            setter_callback=self.active_changed,
        )
        self._effect = tv_service.configure_char(
            'ActiveIdentifier', value=1,
            setter_callback=self.identifier_changed,
        )
      
        tv_service.configure_char('Name', value=self.NAME)
        tv_service.configure_char('ConfiguredName', value=self.NAME)
        tv_service.configure_char('SleepDiscoveryMode', value=1)
        

        for idx, (source_name, source_type) in enumerate(self.SOURCES.items()):
            input_source = self.add_preload_service('InputSource', ['Name', 'Identifier'])
            input_source.configure_char('Name', value=source_name)
            input_source.configure_char('Identifier', value=idx + 1)
            input_source.configure_char('ConfiguredName', value=source_name)
            input_source.configure_char('InputSourceType', value=source_type)
            input_source.configure_char('IsConfigured', value=1)
            input_source.configure_char('CurrentVisibilityState', value=0)

            tv_service.add_linked_service(input_source)


    def set_state(self, value):
        logger.info(f"set_state: {value}")
        self.accessory_state = value
        if value == 1:  # On
            self.set_hue(self.hue)
        else:
            resp = self.api.on_off(False)
            self._active.value = 0
            self._active.notify()
            logger.info(f"[State] API: {resp}")
           

    def set_hue(self, value):
        logger.info(f"set_hue: {value}")
        self._active.value = 0
        self._active.notify()
        if self.accessory_state == 1:
            self.hue = value
            self.char_hue.value = self.hue
            self.char_hue.notify()
            rgb_tuple = self.hsv_to_rgb(
                self.hue, self.saturation, 100)
            resp = self.api.set_color(rgb_tuple,self.brightness)
            logger.info(f"[Hue] API: {resp}")
        else:
            self.hue = value  

    def set_brightness(self, value):
        self.brightness = value
        self.char_bri.value = value
        self.char_bri.notify()
        logger.info(f"set_brightness: {value}")
        self.set_hue(self.hue)
        

    def set_saturation(self, value):
        self.saturation = value
        logger.info(f"set_saturation: {value}")
        self.set_hue(self.hue)
        

    def hsv_to_rgb(self, h, s, v):
   
        h_ = h / 60
        s = s / 100
        v = v / 100


        C = v * s  
        X = C * (1 - abs(h_ % 2 - 1))

        RGB = [0.0, 0.0, 0.0]

        if 0 <= h_ <= 1:
            RGB = [C, X, 0]
        elif 1 <= h_ <= 2:
            RGB = [X, C, 0]
        elif 2 <= h_ <= 3:
            RGB = [0, C, X]
        elif 3 <= h_ <= 4:
            RGB = [0, X, C]
        elif 4 <= h_ <= 5:
            RGB = [X, 0, C]
        elif 5 <= h_ <= 6:
            RGB = [C, 0, X]
        else:
            RGB = [0, 0, 0]

        m = v - C

        return int( round(((RGB[0] + m) * 255),0) ),int( round(((RGB[1] + m) * 255),0) ), int( round(((RGB[2] + m) * 255),0) )

    def rgb_to_hsv(self,rgb):
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]

        r_ = r / 255
        g_ = g / 255
        b_ = b / 255

        cmax = max(r_,g_,b_)
        cmin = min(r_,g_,b_)

        d = cmax -cmin

        #### calc hue ####
        if d == 0:
            H = 0
        elif cmax == r_:
            H = 60 * (((g_ -b_ )/ d) % 6 )
        elif cmax == g_:
            H = 60 * (((b_ - r_) / d) +2 )
        elif cmax == b_:
            H = 60 * (((r_ -g_) / d) + 4)
        else:
            print("nothing fits")

        #### calc s ####
        if cmax == 0:
            S = 0
        else:
            S = (d / cmax)

        return int(round(H,0)),int(round(S*100,0)),int(round(cmax*100,0))

    def active_changed(self, value):
        logger.info('Turn %s' % ('on' if value else 'off'))
        if self._active.value:
            logger.info(f"Sending effect {list(self.SOURCES.keys())[self._effect.value-1]}")
            if self.accessory_state:
                self.api.set_effect(list(self.SOURCES.keys())[self._effect.value-1])
            else:
                self._active.value = 0
                self._active.notify()
        else:
            self.set_hue(self.hue)

    def identifier_changed(self, value):
        logger.info('Change input to %s' % list(self.SOURCES.keys())[value-1])
        self.api.set_effect(list(self.SOURCES.keys())[value-1])
        self._effect.value = value

    @Accessory.run_at_interval(60)
    def run(self):
        try:
            status, current_state = self.api.get_status()
            if status == 200:
                state = current_state['on']
                v = int(round(((current_state['bri'] / 255) * 100), 0))
                color = tuple(current_state['seg'][0]['col'][0])
                h, s, __ = self.rgb_to_hsv(color)
                logger.info("Updating:")
                logger.info(f"Neopixel: state={state}    | hue={h}    | brightness={v}    | saturation={s}")
                logger.info(f"Bridge  : state={self.char_on.value}    | hue={self.char_hue.value}    | brightness={self.char_bri.value}    | saturation={self.char_saturation.value}")
                         
                if self.accessory_state != state :
                    print(state)
                    if state == False: #light was turned off
                        self.char_on.value = state
                        self.accessory_state = state 
                        self.char_on.notify()
                    else: #light was turned on
                        self.char_on.value = state
                        self.char_bri.value = v
                        self.char_hue.value = h 
                        self.char_saturation.value = s
                        self.brightness = v
                        self.saturation = s 
                        self.hue = h
                        self.accessory_state = state
                        self.char_bri.notify()
                        self.char_saturation.notify()
                        self.char_hue.notify()
                        self.char_on.notify()
                elif (self.hue != h or self.brightness != v or self.saturation != s) and self._active.value == False:
                    if self.accessory_state == 1:
                        self.char_bri.value = v
                        self.char_hue.value = h 
                        self.char_saturation.value = s
                        self.brightness = v
                        self.saturation = s 
                        self.hue = h
                        self.char_bri.notify()
                        self.char_saturation.notify()
                        self.char_hue.notify()
        except:
            logger.info("Unable to fetch WLED state")
                    
                    

         

