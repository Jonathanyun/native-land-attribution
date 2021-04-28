Native Land Attribution Quickie for Hack for LA
-----------------------------------------------

    ## Load libraries
    library(tabulizer) # for extracting tables from PDFs
    library(jsonlite) # for neatly converting JSON to dataframes
    library(stringr) # for string splitting
    library(dplyr) # for data transformations/aggregations
    library(ggplot2) # for plotting
    library(httr) # for raw API calls
    library(ggmap) # easy interface to Google Geocode API

#### Parse Zip Code lookup table from LA County’s official PDF

Using Tabulizer library to extract tables from a PDF, then previewing
the data.

    ## Parse the Zip code lookup table from LA County's PDF at: http://file.lacounty.gov/SDSInter/lac/1031552_MasterZipCodes.pdf
    zips <- extract_tables("http://file.lacounty.gov/SDSInter/lac/1031552_MasterZipCodes.pdf")

    ## Preview
    head(zips[[1]])

    ##      [,1]                                        [,2]                          
    ## [1,] ""                                          "County of Los Angeles"       
    ## [2,] ""                                          "ZIP CODE LIST"               
    ## [3,] ""                                          ""                            
    ## [4,] "ZIP CODE"                                  "AREA NAME * (See note below)"
    ## [5,] "90001 Florence/South Central (City of LA)" ""                            
    ## [6,] "90002 Watts (City of LA)"                  ""                            
    ##      [,3]                    
    ## [1,] ""                      
    ## [2,] ""                      
    ## [3,] "Supervisorial District"
    ## [4,] "1st 2nd 3rd 4th 5th"   
    ## [5,] "X X"                   
    ## [6,] "X"

    head(zips[[2]])

    ##      [,1]    [,2]                                                  [,3] [,4]
    ## [1,] "90047" "South Central (City of LA)"                          ""   "X" 
    ## [2,] "90048" "West Beverly (City of LA)"                           ""   "X" 
    ## [3,] "90049" "Bel Air Estates (City of LA)/Brentwood (City of LA)" ""   ""  
    ## [4,] "90050" "Los Angeles"                                         "X"  ""  
    ## [5,] "90051" "Los Angeles"                                         ""   "X" 
    ## [6,] "90052" "Los Angeles"                                         ""   "X" 
    ##      [,5] [,6] [,7]
    ## [1,] ""   ""   ""  
    ## [2,] "X"  ""   ""  
    ## [3,] "X"  ""   ""  
    ## [4,] ""   ""   ""  
    ## [5,] ""   ""   ""  
    ## [6,] ""   ""   ""

    head(zips[[7]])

    ##      [,1]                             [,2] [,3]
    ## [1,] "91301 Agoura/Oak Park"          "X"  ""  
    ## [2,] "91302 Calabasas/Hidden Hills"   "X"  ""  
    ## [3,] "91303 Canoga Park (City of LA)" "X"  ""  
    ## [4,] "91304 Canoga Park (City of LA)" "X"  "X" 
    ## [5,] "91305 Canoga Park (City of LA)" "X"  ""  
    ## [6,] "91306 Winnetka (City of LA)"    "X"  ""

#### Clean up, normalize, and merge zip tables

Header and column detection were a little problematic on a few pages,
but the errors fall within a limited range of classes and the data is
still usable. Therefore, let’s just trim to what we need. This
involves…  
+ Grabbing only the first two columns per table (given the commonality
between the errors)  
+ Remove all rows that don’t start with a zip code  
+ For all those rows with zip and area name merged, split the text and
replace  
+ Flag areas that are officially part of the City of LA


    ## Generally, between the different types of errors we're seeing, the data we need is in the first 2 columns of the listed matrices, so let's row bind the first two columns of all the matrices
    zips_df <- data.frame()
    for(i in 1:length(zips)){
        zip_page <- as.data.frame(zips[i])[,c(1:2)]
        zips_df <- rbind(zips_df, zip_page)
    }

    ## Pretty the names and remove rows that don't start with 5 numbers, then preview
    names(zips_df) <- c("zip","area_name")
    zips_df <- zips_df[grep("^[0-9][0-9][0-9][0-9][0-9].*", as.character(zips_df$zip)),]
    head(zips_df)

    ##                                          zip area_name
    ## 5  90001 Florence/South Central (City of LA)          
    ## 6                   90002 Watts (City of LA)          
    ## 7           90003 South Central (City of LA)          
    ## 8            90004 Hancock Park (City of LA)          
    ## 9               90005 Koreatown (City of LA)          
    ## 10           90006 Pico Heights (City of LA)

    tail(zips_df)

    ##                                 zip area_name
    ## 486                  93560 Rosamond         X
    ## 487                  93563 Valyermo         X
    ## 488                 93584 Lancaster         X
    ## 489                 93586 Lancaster         X
    ## 490                  93590 Palmdale         X
    ## 491 93591 Palmdale/Lake Los Angeles         X

    ## How many rows have zip and area name merged?
    zips_df$zip <- as.character(zips_df$zip)
    zips_df$area_name <- as.character(zips_df$area_name)
    length(zips_df$zip[grep(" [aA-zZ]", zips_df$zip)])

    ## [1] 175

    ## For all those rows with zip and area name merged, split the text and replace
    zips_df[grep(" [aA-zZ]", zips_df$zip),] <- str_split_fixed(zips_df$zip[grep(" [aA-zZ]", zips_df$zip)], " ", n = 2)
    dim(zips_df)

    ## [1] 487   2

    ## Flag whether an area is in the "City of LA" (vs in-line text), to clean and lean things out
    zips_df$LA_city <- grepl("City of LA", zips_df$area_name, ignore.case = T)
    zips_df$area_name <- gsub("\\(City of LA\\)| \\(City of LA\\)", "", zips_df$area_name, ignore.case = T)

    ## Preview final data
    head(zips_df)

    ##      zip              area_name LA_city
    ## 5  90001 Florence/South Central    TRUE
    ## 6  90002                  Watts    TRUE
    ## 7  90003          South Central    TRUE
    ## 8  90004           Hancock Park    TRUE
    ## 9  90005              Koreatown    TRUE
    ## 10 90006           Pico Heights    TRUE

    tail(zips_df)

    ##       zip                 area_name LA_city
    ## 486 93560                  Rosamond   FALSE
    ## 487 93563                  Valyermo   FALSE
    ## 488 93584                 Lancaster   FALSE
    ## 489 93586                 Lancaster   FALSE
    ## 490 93590                  Palmdale   FALSE
    ## 491 93591 Palmdale/Lake Los Angeles   FALSE

#### Geocode (lat, lon) L.A. County zips using Google’s Geocoding API

Unfortunately, this API is rate-limited, so we’ll factor that into our
design.

    if(!file.exists("dat/los-angeles_county_zip-codes_lat-lon.csv")){
      
        ## Grab my Google Geocode API key and register it with GGmaps, my easy interface to Google Maps family of APIs
        geo_key <- readRDS("geo_key.RDS")
        register_google(geo_key)
        
        ## Run zips through Geocode API call and keep lat/lon as new column values per zip
        zips_df[, c("lon", "lat")] <- geocode(zips_df$zip, output = "latlon")
        
        ## Save table for later use
        write.csv(zips_df, "dat/los-angeles_county_zip-codes_lat-lon.csv", row.names = F)
        
    } else {
      
        ## Let user know we've already got the data and therefore don't need to call the API
        print("Zip to Lat/Lon lookup table already exists. Skipping API call, then previewing data...")
      
        ## Get existing data, if it's there
        zips_df <- read.csv("dat/los-angeles_county_zip-codes_lat-lon.csv", stringsAsFactors = F)
      
    }

    ## [1] "Zip to Lat/Lon lookup table already exists. Skipping API call, then previewing data..."

    ## Preview the data
    head(zips_df)

    ##     zip              area_name LA_city       lon      lat
    ## 1 90001 Florence/South Central    TRUE -118.2468 33.96979
    ## 2 90002                  Watts    TRUE -118.2497 33.95111
    ## 3 90003          South Central    TRUE -118.2731 33.96580
    ## 4 90004           Hancock Park    TRUE -118.3082 34.07489
    ## 5 90005              Koreatown    TRUE -118.3097 34.05788
    ## 6 90006           Pico Heights    TRUE -118.2965 34.04708

    tail(zips_df)

    ##       zip                 area_name LA_city       lon       lat
    ## 482 93560                  Rosamond   FALSE -118.3228 34.884301
    ## 483 93563                  Valyermo   FALSE -117.7491 34.405338
    ## 484 93584                 Lancaster   FALSE -118.1400 34.700000
    ## 485 93586                 Lancaster   FALSE  110.3391  1.542587
    ## 486 93590                  Palmdale   FALSE -118.0600 34.500000
    ## 487 93591 Palmdale/Lake Los Angeles   FALSE -117.8194 34.592562

    ## Any NAs?
    print("Possible problem zips, for inspection:")

    ## [1] "Possible problem zips, for inspection:"

    zips_df[is.na(zips_df$lon),]

    ##      zip        area_name LA_city lon lat
    ## 79 90080 Airport Worldway    TRUE  NA  NA

#### Send lat, lons to Native-land.ca API for list of Native lands LA County currently covers

    ## Test API call
    test <- GET(paste0("https://native-land.ca/api/index.php?maps=languages,territories?positions=", zips_df$lat[1], ",", zips_df$lon[1]))
    test            

    ## Response [https://native-land.ca/resources/api-docs/?maps=languages%2Cterritories%3Fpositions%3D33.9697897%2C-118.2468148]
    ##   Date: 2021-04-28 22:21
    ##   Status: 403
    ##   Content-Type: text/html; charset=UTF-8
    ##   Size: 26.5 kB
    ## <!DOCTYPE html>
    ## <html lang="en">
    ## <head>
    ## <meta charset="utf-8">
    ## <meta name="viewport" content="width=device-width, initial-scale=1">
    ## <link rel="shortcut icon" href="https://native-land.ca/wp/wp-content/themes/N...
    ## <title>Native-Land.ca | Our home on native land</title>
    ## <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    ## <meta charset="utf-8">
    ## <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
    ## ...
