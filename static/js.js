$(function() {
    // TODO check all lets and maybe make them consts
    // TODO check all variables and maybe make them lets or consts or back to var?
    let maxHeight = $(window).height();
    let maxWidth = $(window).width();
    let maxX;
    let maxY;
    let svg;
    $("#import").click(function() {
        // TODO
        /*if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
          alert('The File APIs are not fully supported in this browser.');
          return;
        }

        input = document.getElementById('fileinput');
        if (!input) {
          alert("Um, couldn't find the fileinput element.");
        }
        else if (!input.files) {
          alert("This browser doesn't seem to support the `files` property of file inputs.");
        }
        else if (!input.files[0]) {
          alert("Please select a file before clicking 'Load'");
        } else {*/
        let file = $("#file")[0].files[0];
        let reader = new FileReader();

        let senddata = new Object();
        senddata.name = file.name;
        senddata.date = file.lastModified;
        senddata.size = file.size;
        senddata.type = file.type;

        reader.onload = function(theFileData) {
            senddata.fileData = theFileData.target.result;
            console.log(senddata.fileData);
            load("post", {
                file: senddata.fileData
            });
        }

        reader.readAsDataURL(file);
        // }

    });

    //load("post", {file: "data:application/octet-stream;base64,KCgoQTowLjQsQjowLjUpRTowLjIsRjowLjMpSTowLjEsKEc6MC4zLChDOjAuMyxEOjAuNClIOjAuNClKOjAuMik7"});
    //load("post", {file: "data:application/octet-stream;base64,KCgoQTowLjQsQjowLjUpOjAuMixGOjAuMyk6MC4xLChHOjAuMywoQzowLjMsRDowLjQpOjAuNCk6MC4yKTs="});

    function load(method, httpData) {
        if (method == "post") {
            $.post("load", httpData, update);
        } else {
            $.get("load", httpData, update);
        }
    }

    function update(data, status) {
        //alert("Data: " + data + "\nStatus: " + status);
        console.log(data);
        draw(JSON.parse(data["tree"]));
        snapshots(data["trees"]);
    }

    function draw(data) {
        console.log(data);
        let g;

        if (typeof svg !== "undefined") {
            svg.remove();
        }

        svg = Snap(maxWidth, maxHeight);
        $(svg.node).appendTo($("#mainDiv"));

        extraData = data.pop();

        maxDistance = extraData["max_distance"];
        longestName = extraData["longest_name"];

        let fontSize = '1.375em';
        let strokeWidth = 4;

        longestNameTester = svg.text(0, 0, longestName).attr({
            fontSize: fontSize
        });
        longestNameWidth = Math.ceil(longestNameTester.getBBox().width);
        longestNameTester.remove();

        // TODO instead of checking longest name, we have to check longest combination of line with distance and name for each and get longest total line

        amount = data.length;

        offset = 10;
        //scaleX = 200;
        scaleX = 500;
        scaleY = 30;

        svg.remove();
        //svg = Snap(((scaleX * maxDistance) + (2.5 * offset) + longestNameWidth), (scaleY * (amount + 1)));
        //$(svg.node).appendTo($("#mainDiv"));
        maxX = (scaleX * maxDistance) + (2.5 * offset) + longestNameWidth;
        maxY = scaleY * (amount + 1);
        svg = Snap(maxWidth, maxHeight);
        $(svg.node).appendTo($("#mainDiv"));
        g = svg.g();
        lines = g.g();
        g.add(svg.path("M0,0H" + maxX + "V" + maxY + "H0V0").attr({
            fill: 'none',
            stroke: 'black',
            strokeWidth: 2
        }));

        // TODO write this nicer
        topBottom = [-5, maxY + 15];
        let topBottomLine;
        topBottom.forEach(function(value) {
            for (var i = 0; i < maxDistance * 10; i++) {
                topBottomLine = svg.line(10 + scaleX * i / 10, value - 10, 10 + scaleX * i / 10, value).attr({
                    fill: 'none',
                    stroke: 'black',
                    strokeWidth: 2
                });
                topBottomLine.append(Snap.parse('<title>' + i / 10 + '</title>'));
                lines.add(topBottomLine);
                // TODO could be put exactly in the middle, now only puts the beginning above the line
                // g.add(svg.text(10 + scaleX * i, value - 20, i + ".0").attr({dominantBaseline: 'middle', fontSize: fontSize}));
            }
            topBottomLine = svg.line(10 + scaleX * maxDistance, value - 10, 10 + scaleX * maxDistance, value).attr({
                fill: 'none',
                stroke: 'black',
                strokeWidth: 2
            });
            topBottomLine.append(Snap.parse('<title>' + maxDistance + '</title>'));
            lines.add(topBottomLine);
            // TODO could be put exactly in the middle, now only puts the beginning above the line
            // g.add(svg.text(10 + scaleX * maxDistance, value - 20, maxDistance).attr({dominantBaseline: 'middle', fontSize: fontSize}));
            lines.add(svg.line(10, value - 5, 10 + scaleX * maxDistance, value - 5).attr({
                fill: 'none',
                stroke: 'black',
                strokeWidth: 2
            }));
        });
        for (var i = 0; i < maxDistance * 10; i++) {
            topBottomLine = svg.line(10 + scaleX * i / 10, topBottom[0], 10 + scaleX * i / 10, topBottom[1] - 10).attr({
                fill: 'none',
                stroke: 'black',
                strokeWidth: 2,
                strokeOpacity: 0.125
            });
            topBottomLine.append(Snap.parse('<title>' + i / 10 + '</title>'));
            lines.add(topBottomLine);
        }
        topBottomLine = svg.line(10 + scaleX * maxDistance, topBottom[0], 10 + scaleX * maxDistance, topBottom[1] - 10).attr({
            fill: 'none',
            stroke: 'black',
            strokeWidth: 2,
            strokeOpacity: 0.125
        });
        topBottomLine.append(Snap.parse('<title>' + maxDistance + '</title>'));
        lines.add(topBottomLine);

        //svg.mousedown(funcMouseDown);
        //svg.mouseup(funcMouseUp);
        //svg.mousemove(funcMouseMove);

        //scaleX = (maxWidth - longestNameWidth - (2.5 * offset)) / maxDistance;
        //scaleY = maxHeight / (amount + 1);

        //let paths = [];

        let hoveredPath;
        let hoveredLine;
        let clickedPath;
        let nameText;

        data.forEach(function(item, index, array) {
            if (item["name"] != "None") {
                // TODO draw all texts at the right
                // with path stroke dasharray
                //g.add(svg.text(item["total_distance"] * scaleX + (1.5 * offset), (index + 1) * scaleY, item["name"]).attr({dominantBaseline: 'middle', fontSize: fontSize, 'data-id': item["id"]}));
                nameText = svg.text(maxX - offset, (index + 1) * scaleY, item["name"]).attr({
                    dominantBaseline: 'middle',
                    fontSize: fontSize,
                    'data-id': item["id"],
                    textAnchor: 'end'
                });
                g.add(nameText);
                if (item["total_distance"] * scaleX + (1.5 * offset) < maxX - (1.5 * offset) - Math.ceil(nameText.getBBox().width) - offset) {
                    g.add(svg.line(item["total_distance"] * scaleX + (1.5 * offset), (index + 1) * scaleY, maxX - (1.5 * offset) - Math.ceil(nameText.getBBox().width), (index + 1) * scaleY).attr({
                        fill: 'none',
                        stroke: 'black',
                        strokeWidth: 2,
                        strokeDasharray: 4
                    }));
                }
            } else {
                if (item["bootstrap"] != "None" && item["bootstrap"] != "") {
                    parent = array.findIndex((elem)=>elem.id == item["parent"]);
                    // TODO could be put exactly in the middle, now only puts the beginning in the middle
                    g.add(svg.text((parseFloat(array[parent]["total_distance"]) + (item["distance"] / 2)) * scaleX, (index + 1) * scaleY, item["bootstrap"]).attr({
                        dominantBaseline: 'baseline',
                        fontSize: 0.5 * fontSize,
                        'data-id': item["id"]
                    }));
                    // TODO data-id added graying out of child bootstraps but not selected bootstrap
                }

                l_child = array.findIndex((elem)=>elem.id == item["l_child"]);
                r_child = array.findIndex((elem)=>elem.id == item["r_child"]);

                mX = (item["total_distance"] * scaleX) + offset;
                mYLeft = (index + 1) * scaleY - strokeWidth;
                mYRight = (index + 1) * scaleY + strokeWidth;

                if (item["id"] == 0) {
                    mYLeft += strokeWidth / 2;
                    mYRight -= strokeWidth / 2;
                }

                vLeft = (l_child + 1) * scaleY;
                vRight = (r_child + 1) * scaleY;
                hLeft = array[l_child]["total_distance"] * scaleX + offset;
                hRight = array[r_child]["total_distance"] * scaleX + offset;

                left = svg.path("M" + mX + "," + mYLeft + "V" + vLeft + "H" + hLeft).attr("data-id", array[l_child]["id"]);
                right = svg.path("M" + mX + "," + mYRight + "V" + vRight + "H" + hRight).attr("data-id", array[r_child]["id"]);
                g.add(left, right);

                if (array[l_child]["bootstrap"] != "") {
                    left.append(Snap.parse('<title>' + array[l_child]["bootstrap"] + '</title>'));
                }
                if (array[r_child]["bootstrap"] != "") {
                    right.append(Snap.parse('<title>' + array[r_child]["bootstrap"] + '</title>'));
                }

                if (("l_child"in array[l_child]) && ("r_child"in array[l_child])) {
                    left.attr({
                        "data-l_child": array[l_child]["l_child"],
                        "data-r_child": array[l_child]["r_child"]
                    });
                }
                if (("l_child"in array[r_child]) && ("r_child"in array[r_child])) {
                    right.attr({
                        "data-l_child": array[r_child]["l_child"],
                        "data-r_child": array[r_child]["r_child"]
                    });
                }

                paths = [left, right];

                paths.forEach(function(itemPath, indexPath, arrayPath) {
                    itemPath.attr({
                        fill: 'none',
                        stroke: 'black',
                        strokeWidth: strokeWidth,
                        strokeLinecap: 'square'
                    });
                    itemPath.mouseover(function() {
                        itemPath.attr({
                            stroke: 'dodgerblue',
                            strokeWidth: strokeWidth * 2
                        });
                        if (typeof hoveredPath === "undefined" || (typeof hoveredPath === "object" && !hoveredPath)) {
                            hoveredPath = itemPath.use().attr({
                                pointerEvents: 'none'
                            });
                        }
                    });
                    itemPath.mouseout(function() {
                        itemPath.attr({
                            stroke: 'black',
                            strokeWidth: strokeWidth
                        });
                        hoveredPath.remove();
                        hoveredPath = null;
                    });
                    itemPath.click(function() {
                        if (typeof clickedPath === "undefined" || (typeof clickedPath === "object" && !clickedPath)) {
                            hoveredPath.remove();
                            clickedPath = itemPath;
                            itemPath.attr({
                                strokeOpacity: 0.25
                            });
                            childrenIds = [itemPath.attr("data-l_child"), itemPath.attr("data-r_child")];
                            while ((typeof childrenIds !== "undefined") && (childrenIds.length > 0)) {
                                childId = childrenIds.shift();
                                childPath = svg.select("path[data-id='" + childId + "']");
                                if (childPath) {
                                    childPath.attr({
                                        strokeOpacity: 0.25,
                                        pointerEvents: 'none'
                                    });
                                    if (childPath.attr("data-l_child") && childPath.attr("data-r_child")) {
                                        childrenIds.push(childPath.attr("data-l_child"), childPath.attr("data-r_child"));
                                    }
                                }
                                childText = svg.select("text[data-id='" + childId + "']");
                                if (childText) {
                                    childText.attr({
                                        opacity: 0.25,
                                        pointerEvents: 'none'
                                    });
                                }
                            }
                        } else if (clickedPath == itemPath) {
                            hoveredPath.remove();
                            clickedPath = null;
                            itemPath.attr({
                                strokeOpacity: ''
                            });
                            childrenIds = [itemPath.attr("data-l_child"), itemPath.attr("data-r_child")];
                            while ((typeof childrenIds !== "undefined") && (childrenIds.length > 0)) {
                                childId = childrenIds.shift();
                                childPath = svg.select("path[data-id='" + childId + "']");
                                if (childPath) {
                                    childPath.attr({
                                        strokeOpacity: '',
                                        pointerEvents: ''
                                    });
                                    if (childPath.attr("data-l_child") && childPath.attr("data-r_child")) {
                                        childrenIds.push(childPath.attr("data-l_child"), childPath.attr("data-r_child"));
                                    }
                                }
                                childText = svg.select("text[data-id='" + childId + "']");
                                if (childText) {
                                    childText.attr({
                                        opacity: '',
                                        pointerEvents: ''
                                    });
                                }
                            }
                        } else {
                            load("get", {
                                'from': clickedPath.attr("data-id"),
                                'to': itemPath.attr("data-id")
                            });
                            console.log({
                                'from': clickedPath.attr("data-id"),
                                'to': itemPath.attr("data-id")
                            });
                        }
                    });

                    /*itemPath.drag(function(dx, dy, x, y, event) {
                        // TODO does not have to be set every frame
                        pos = itemPath.attr("d");
                        posX = pos.split("H")[1];
                        posY = pos.split("H")[0].split("V")[1];
                        hoveredLine.remove();
                        hoveredLine = svg.line(posX, posY, x, y);
                        hoveredLine.attr({stroke: 'black', strokeWidth: strokeWidth});
                        console.log("move");
                    }, function(x, y, event) {
                        pos = itemPath.attr("d");
                        posX = pos.split("H")[1];
                        posY = pos.split("H")[0].split("V")[1];
                        hoveredPath.remove();
                        itemPath.remove();
                        hoveredLine = svg.line(posX, posY, x, y);
                        hoveredLine.attr({stroke: 'black', strokeWidth: strokeWidth});
                        console.log("start");
                    }, function(event) {
                        console.log("stop");
                    });*/

                });
            }
        });

        // TODO think of the boundaries!
        var startX, startY;
        let move;
        let step = 0.1;

        function funcMouseDown(event) {
            startX = event.clientX;
            startY = event.clientY;
            move = true;
            // TODO only when existing?
            $("svg").css("cursor", "move");
        }

        function funcMouseUp(event) {
            move = false;
            // TODO only when existing?
            $("svg").removeAttr("style");
        }

        function funcMouseMove(event) {
            /*console.log(event.which + event.ctrlKey + event.clientX + event.clientY);*/

            if (move) {
                let offsetX = event.clientX - startX;
                let offsetY = event.clientY - startY;

                currentX = getTransform("x");
                currentY = getTransform("y");

                moveX = currentX + offsetX;
                moveY = currentY + offsetY;

                setTransform("translate", moveX, moveY);
                startX = event.clientX;
                startY = event.clientY;
            }
        }

        function funcWheel(event) {
            currentDeltaY = getTransform("scale");

            posX = event.originalEvent.clientX;
            posY = event.originalEvent.clientY;

            if (posX == 0) {
                posX = 1;
            }

            if (posY == 0) {
                posY = 1;
            }

            let offsetX = (posX / maxWidth - 0.5) * step * maxWidth;
            let offsetY = (posY / maxHeight - 0.5) * step * maxHeight;

            if (event.originalEvent.deltaY < 0) {
                deltaY = currentDeltaY + step;
                offsetX = -offsetX;
                offsetY = -offsetY;
            } else {
                deltaY = currentDeltaY - step;
            }

            currentX = getTransform("x");
            currentY = getTransform("y");

            moveX = currentX + offsetX;
            moveY = currentY + offsetY;

            //setTransform("scale", deltaY, moveX, moveY);
            setTransform("scale", deltaY);
        }

        function setTransform() {
            originalTranslateX = getTransform("x");
            originalTranslateY = getTransform("y");
            originalScale = getTransform("scale");

            if (arguments[0] == "translate") {
                scale = originalScale;
                translateX = arguments[1];
                translateY = arguments[2];
            } else if (arguments[0] == "scale") {
                scale = arguments[1];
                translateX = 100 * scale;
                //arguments[2]; // TODO
                translateY = 100 * scale;
                //arguments[3]; // TODO

                minScale = 0.1;
                maxScale = 2;

                if (scale < minScale) {
                    scale = minScale;
                    translateX = originalTranslateX;
                    translateY = originalTranslateY;
                } else if (scale > maxScale) {
                    scale = maxScale;
                    translateX = originalTranslateX;
                    translateY = originalTranslateY;
                }
            }

            minTranslateX = 0;
            minTranslateY = 0;
            maxTranslateX = maxWidth - maxX * scale;
            maxTranslateY = maxHeight - maxY * scale;

            // TODO hinder moving to far into any direction
            // TODO zooming needs finetuning

            /*if (translateX < minTranslateX) {
                translateX = minTranslateX;
            } else if (translateX > maxTranslateX) {
                translateX = maxTranslateX;
            }

            if (translateY < minTranslateY) {
                translateY = minTranslateY;
            } else if (translateY > maxTranslateY) {
                translateY = maxTranslateY;
            }*/

            g.transform("translate(" + translateX + " " + translateY + ") scale(" + scale + " " + scale + ")");
        }

        function getTransform() {
            if (g.transform().total !== "") {
                currentTransform = g.transform().totalMatrix;
                translateX = parseFloat(currentTransform["e"]);
                translateY = parseFloat(currentTransform["f"]);
                scale = parseFloat(currentTransform["a"]);
            } else {
                translateX = 0;
                translateY = 0;
                scale = 1;
            }
            switch (arguments[0]) {
            case "x":
                return translateX;
            case "y":
                return translateY;
            case "scale":
                return scale;
            }
        }

        $(svg.node).mousedown(funcMouseDown);
        $(svg.node).mouseup(funcMouseUp);
        $(svg.node).mousemove(funcMouseMove);
        $(svg.node).on("wheel", funcWheel);
    }

    function snapshots(data) {
        console.log(data);
        $("#no-entries").remove();
        $("#snapshots").empty();
        $("#snapshots").append('<thead><tr><th scope="col">#</th><th scope="col">JSON</th><th scope="col">DateTime</th></tr></thead>');
        $("#snapshots").append('<tbody>');
        data.forEach(function(value) {
            $("#snapshots").append('<tr><th scope="row">' + value[0] + '</th><td>LINK'/*+ value[1]*/
            + '</td><td>' + value[2] + '</td></tr>');
        });
        $("#snapshots").append('</tbody>');
    }

    var onOffBtn1 = "off";
    var onOffBtn2 = "off";
    var exnum = 0;
    var num = 0;

    $("#btnClose").click(function() {
        onOffBtn1 = "off";
        onOffBtn2 = "off";
        exnum = 0;
        num = 0;
        $("#tab1").hide("fast");
        $("#tab2").hide("fast");
    });

    $("#btn1").click(function() {
        num = 1;
        switch (onOffBtn1) {
        case "off":
            {
                $("#tab" + exnum).hide("fast");
                $("#tab" + num).show("fast");
                onOffBtn2 = "off";
                onOffBtn1 = "on";
                exnum = 1;
                break;
            }
        case "on":
            {
                $("#tab" + num).hide("fast");
                $("#tab" + exnum).hide("fast");
                onOffBtn2 = "off";
                onOffBtn1 = "off";
                break;
            }
        }
    });

    $("#btn2").click(function() {
        num = 2;
        switch (onOffBtn2) {
        case "off":
            {
                $("#tab" + exnum).hide("fast");
                $("#tab" + num).show("fast");
                onOffBtn1 = "off";
                onOffBtn2 = "on";
                exnum = 2;
                break;
            }
        case "on":
            {
                $("#tab" + num).hide("fast");
                $("#tab" + exnum).hide("fast");
                onOffBtn2 = "off";
                onOffBtn1 = "off";
                break;
            }
        }
    });
});

/*$(window).resize(function() {
    svg.size($(window).width(), $(window).height());
});*/
