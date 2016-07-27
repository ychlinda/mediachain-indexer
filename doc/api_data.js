define({ "api": [  {    "type": "post",    "url": "/search",    "title": "Search for images",    "name": "PostSearch",    "group": "Search",    "version": "0.1.0",    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "q",            "description": "<p>Query text</p>"          },          {            "group": "Parameter",            "type": "Number",            "optional": true,            "field": "limit",            "description": "<p>Maximum number of results to return.</p>"          }        ]      },      "examples": [        {          "title": "Request-Example:",          "content": "{\"q\":\"crowd\", \"limit\":5}",          "type": "json"        }      ]    },    "description": "<p>Must be sent as HTTP form parameter: <code>curl &quot;http://api.mediachainlabs.com/search&quot; --form 'json={&quot;q&quot;:&quot;crowd&quot;, &quot;limit&quot;:5}'</code></p>",    "success": {      "fields": {        "Success 200": [          {            "group": "Success 200",            "type": "Object",            "optional": true,            "field": "next_page",            "description": "<p>Parameters to query next page.</p>"          },          {            "group": "Success 200",            "type": "Number",            "optional": false,            "field": "next_page.limit",            "description": ""          },          {            "group": "Success 200",            "type": "Number",            "optional": false,            "field": "next_page.offset",            "description": ""          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "next_page.token",            "description": "<p>Unique token representing this query.</p>"          },          {            "group": "Success 200",            "type": "Object",            "optional": true,            "field": "prev_page",            "description": "<p>Parameters to query previous page.</p>"          },          {            "group": "Success 200",            "type": "Number",            "optional": false,            "field": "prev_page.limit",            "description": ""          },          {            "group": "Success 200",            "type": "Number",            "optional": false,            "field": "prev_page.offset",            "description": ""          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "prev_page.token",            "description": "<p>Unique token representing this query.</p>"          },          {            "group": "Success 200",            "type": "Object[]",            "optional": false,            "field": "results",            "description": "<p>Array of image results.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "results._id",            "description": "<p>Unique id of image record.</p>"          },          {            "group": "Success 200",            "type": "Number",            "optional": false,            "field": "results._score",            "description": "<p>Relevancy of image to query.</p>"          },          {            "group": "Success 200",            "type": "Object",            "optional": false,            "field": "results._source",            "description": "<p>Metadata for image.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": true,            "field": "results._source.artist_name",            "description": "<p>Attribution for creator.</p>"          },          {            "group": "Success 200",            "type": "String[]",            "optional": false,            "field": "results._source.keywords",            "description": "<p>Keywords describing image.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "results._source.date_created",            "description": "<p>Date of creation.</p>"          },          {            "group": "Success 200",            "type": "Object",            "optional": false,            "field": "results._source.origin",            "description": ""          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "results._source.origin.name",            "description": "<p>Name of origin.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "results._source.origin.url",            "description": "<p>Permalink for image at origin.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "results._source.image_url",            "description": "<p>Hi-res image url.</p>"          },          {            "group": "Success 200",            "type": "Object",            "optional": false,            "field": "results._source.license",            "description": "<p>Image license.</p>"          },          {            "group": "Success 200",            "type": "Object",            "optional": false,            "field": "results._source.license.name",            "description": "<p>License name.</p>"          },          {            "group": "Success 200",            "type": "Object",            "optional": false,            "field": "results._source.license.url",            "description": "<p>License url.</p>"          }        ]      },      "examples": [        {          "title": "Exampe data on success:",          "content": "{\n  \"next_page\": {\n    \"limit\": 20,\n    \"offset\": 20,\n    \"token\": \"6175f4c9c667cc4b7da6ac64685600bc\"\n  },\n  \"prev_page\": null,\n  \"results\": [\n    {\n      \"_id\": \"f6c135226adb11a7233cab4357af35f6\",\n      \"_score\": 20,\n      \"_source\": {\n        \"artist_name\": \"Krista Mangulsone\",\n        \"date_created\": null,\n        \"keywords\": [\n          \"love\",\n          \"friends\",\n          \"garden\",\n          \"animal\",\n          \"kiss\",\n          \"dog\",\n          \"cute\",\n          \"pets\",\n          \"relax\",\n          \"cat\",\n          \"lying\",\n          \"friendship\",\n          \"puppy\",\n          \"outdoor\",\n          \"feline\"\n        ],\n        \"license\": {\n            \"name\": \"CC0\",\n            \"name_long\": \"Creative Commons Zero (CC0)\",\n            \"license_url\": null\n        },\n        \"origin\": {\n          \"name\": \"unsplash.com\",\n          \"url\": \"https://www.unsplash.com/photo/orange-tabby-cat-beside-fawn-short-coated-puppy-24104/\"\n        },\n        \"image_url\": {\n          \"url\": \"http://54.209.175.109:6008/pe/8/a/2/5/8a25a2a9c738ebd76043481a457b62a0.jpg\"\n        }\n      }\n    }\n  ],\n  \"results_count\": \"200+\"\n}",          "type": "json"        }      ]    },    "filename": "./mediachain/indexer/mc_web.py",    "groupTitle": "Search"  },  {    "success": {      "fields": {        "Success 200": [          {            "group": "Success 200",            "optional": false,            "field": "varname1",            "description": "<p>No type.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "varname2",            "description": "<p>With type.</p>"          }        ]      }    },    "type": "",    "url": "",    "version": "0.0.0",    "filename": "./doc/main.js",    "group": "_Users_denisnazarov_web_rc_mediachain_indexer_doc_main_js",    "groupTitle": "_Users_denisnazarov_web_rc_mediachain_indexer_doc_main_js",    "name": ""  }] });
