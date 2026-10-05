#initial parameters for startup an application
#author: Łukasz Stolzmann

#COLLZONE DB PARAMETERS
CONNECTION_NAME = 'DSN=YourODBCConnectionName'

#ENC s57 PATHS
DIR = 'maps'
GDYNIA = 'PL5GDYNA.000'
WYBRZEZE = 'PL5MP500.000'

#ADRESSES FOR CONNECTION
# set these to your own AIS feed server address/port
AIS_ADDRESS = 'YOUR_AIS_SERVER_ADDRESS'
AIS_PORT = 0
AIS_ADDRESS_SZWECJA = 'YOUR_SECONDARY_AIS_SERVER_ADDRESS'
AIS_PORT_SZWECJA = 0

GNSS_ADDRESS = 'YOUR_GNSS_SERVER_ADDRESS'
GNSS_PORT = 0

#RADAR NAV PARAMS [NM]
VECTOR_LENGTH = 12
DEFAULT_RANGE = 12
MIN_RANGE = 0.25
MAX_RANGE = 96
RANGE_SCALES = [0.25, 0.5, 0.75, 1.5, 3, 6, 12, 24, 48, 96, 192, 384, 768, 768*2]

#RADAR DISPLAY PARAMS
DISPLAY_MODE = {
    'n_up': 1,
    'h_up': 2
}

MOTION_MODE = {
    'rel': 1,
    'true': 2
}

#network parameters - ais server
ADDRESS = 'YOUR_AIS_SERVER_ADDRESS'
PORT = 0

#OTHERS [undefined]
MOVING_STEP = 0.1
UPDATE_COOLDOWN = 40

#VISUAL [px]
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450 
RADAR_RADIUS = 350 
FONT_COMPONENT = 17
FONT_BUTTON = 16
FONT_INFOBOX = 18
FONT_RADAR = 17
FONT_SLIDER = 22


ENC_COLOR = {
'BCNLAT': '#000000', #Beacon, lateral
'BCNSPP': '#000000', #Beacon, special purpose/general
'BRIDGE': '#000000', #Bridge
'BUISGL': '#000000', #Building, single
'BUAARE': '#F8F48F', #Built-up area
'BOYLAT': '#000000', #Buoy, lateral
'BOYSPP': '#000000', #Buoy, special purpose/general
'CBLSUB': '#ff00ff', #Cable, submarine
'CTNARE': '#000000', #Caution area
'COALNE': '#231f20', #Coastline
'CONVYR': '#000000', #Conveyor
'CRANES': '#000000', #Crane
'DEPARE': '#045FB7', #Depth area
'DEPCNT': '#2A2C2D', #Depth contour
'DRYDOC': '#ffd87d', #Dry dock
'FLODOC': '#ffd87d', #Floating dock
'HRBARE': '#3FDCFC', #Harbour area
'HRBFAC': '#A1A4A8', #Harbour facility
'HULKES': '#000000', #Hulk
'LNDARE': '#ffd87d', #Land area
'LNDRGN': '#ffbd33', #Land region
'LNDMRK': '#000000', #Landmark
'LIGHTS': '#000000', #Light
'MORFAC': '#000000', #Mooring/warping facility
'NAVLNE': '#000000', #Navigation line
'OBSTRN': '#000000', #Obstruction
'PILPNT': '#000000', #Pile
'PIPSOL': '#000000', #Pipeline, submarine/on land
'PONTON': '#000000', #Pontoon
'PYLONS': '#000000', #Pylon/bridge support
'RDOSTA': '#000000', #Radio station
'RAILWY': '#000000', #Railway
'RECTRC': '#000000', #Recommended track
'RSCSTA': '#000000', #Rescue station
'RESARE': '#3ed3ed', #Restricted area
'ROADWY': '#000000', #Road
'SEAARE': '#aae0fa', #Sea area / named water area
'SLCONS': '#000000', #Shoreline Construction
'SILTNK': '#000000', #Silo / tank
'SLOTOP': '#000000', #Slope topline
'SOUNDG': '#ffffff', #Sounding
'TOPMAR': '#000000', #Topmark
'UWTROC': '#000000', #Underwater rock / awash rock
'UNSARE': '#000000', #Unsurveyed area
'VEGATN': '#ffd87d', #Vegetation
'WRECKS': '#000000', #Wreck
'COLLZONE':  '#f21111', #Collzone color 
}

