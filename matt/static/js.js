/*
* MATT - A Framework For Modifying And Testing Topologies
* Copyright (C) 2020 Jeff Raffael Gower
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <https://www.gnu.org/licenses/>.
*/
$(function() {
    // TODO check all lets and maybe make them consts
    // TODO check all variables and maybe make them lets or consts or back to var?
    let maxHeight = $(window).height();
    let maxWidth = $(window).width();
    let maxX;
    let maxY;
    let svg;
    let trees;
    let g;
    let buttons_activated = false;
    let counter_of_trees = 0;

    $("#logo-main").offset({left: maxWidth/2 - $("#logo-main").width()/2, top: maxHeight/2 - $("#logo-main").height()/2});

    getOptions();

    $("#import").click(function() {
        $("#modalLabel").text("Import clicked!")
        $("#modalBody").text("Tree is getting calculated!")
        $("#modal").modal("show");
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
        let alignmentFile = $("#alignment-file")[0].files[0];
        let treeFile = $("#tree-file")[0].files[0];

        let alignmentReader;
        let treeReader;

        let senddataAlignment;
        let senddataTree;

        if (typeof alignmentFile !== "undefined") {
            senddataAlignment = {
                name: alignmentFile.name,
                date: alignmentFile.lastModified,
                size: alignmentFile.size,
                type: alignmentFile.type
            }
            alignmentReader = new FileReader();
            alignmentReader.onload = function(theFileData) {
                senddataAlignment.fileData = theFileData.target.result;
                sendAlignmentAndTree();
            }
            alignmentReader.readAsDataURL(alignmentFile);
        }

        if (typeof treeFile != "undefined") {
            senddataTree = {
                name: treeFile.name,
                date: treeFile.lastModified,
                size: treeFile.size,
                type: treeFile.type
            }
            treeReader = new FileReader();
            treeReader.onload = function(theFileData) {
                senddataTree.fileData = theFileData.target.result;
                sendAlignmentAndTree();
            }
            treeReader.readAsDataURL(treeFile);
        }

        function sendAlignmentAndTree() {
            if ((typeof alignmentFile !== "undefined") && (typeof treeFile !== "undefined")) {
                if ((typeof senddataAlignment.fileData !== "undefined") && (typeof senddataTree.fileData !== "undefined")) {
                    load("post", {
                        alignment: {
                            data: senddataAlignment.fileData,
                            name: senddataAlignment.name
                        },
                        tree: {
                            data: senddataTree.fileData,
                            name: senddataTree.name
                        }
                    });
                }
            } else if ((typeof alignmentFile !== "undefined") && (typeof treeFile === "undefined")) {
                if (typeof senddataAlignment.fileData !== "undefined") {
                    load("post", {
                        alignment: {
                            data: senddataAlignment.fileData,
                            name: senddataAlignment.name
                        }
                    });
                }
            } else if ((typeof alignmentFile === "undefined") && (typeof treeFile !== "undefined")) {
                if (typeof senddataTree.fileData !== "undefined") {
                    load("post", {
                        tree: {
                            data: senddataTree.fileData,
                            name: senddataTree.name
                        }
                    });
                }
            }
        }

        // }

    });

    $("#example-import").click(function() {
        load("post", "example");
    });

    let dnaProtein;
    $("#dna").click(function() {
        $("#dna-options").show();
        $("#protein-options").hide();
        dnaProtein = "dna";
    });
    $("#protein").click(function() {
        $("#protein-options").show();
        $("#dna-options").hide();
        dnaProtein = "protein";
    });
    $("#save-options").click(function() {
        optionsJSON = {
            "enable-lengths": $("#enable-lengths")[0].checked
        }
        if (dnaProtein == "dna") {
            optionsJSON["dna-protein"] = "dna";
            optionsJSON["dna-bsr"] = $("#selectBSR").val();
            optionsJSON["dna-bf"] = $("#selectBF").val();
            optionsJSON["dna-rhas"] = $("#selectDNARHAS").val();
        } else if (dnaProtein == "protein") {
            optionsJSON["dna-protein"] = "protein";
            optionsJSON["protein-aaerm"] = $("#selectAAERM").val();
            optionsJSON["protein-pmm"] = $("#selectPMM").val();
            optionsJSON["protein-aaf"] = $("#selectAAF").val();
            optionsJSON["protein-rhas"] = $("#selectAARHAS").val();
        }
        options(optionsJSON);
    });
    $("#test-snapshots").click(function() {
        var snapshots = [];
        $.each($("#select-snapshots option:selected"), function(){
            snapshots.push($(this).val());
        });
        tests({
            "snapshots": snapshots
        });
    });

    $(".btn").mouseup(function(){
        $(this).blur();
    })


    function getOptions() {
        $.get("get-options", "", function(data) {
            data = JSON.parse(data);
            if (data["enable_lengths"]) {
                $("#enable-lengths").prop("checked", true);
            } else {
                $("#enable-lengths").prop("checked", false);
            }
            if (data["dna_protein"] == "dna") {
                dnaProtein = "dna";
                $("#dna").prop("checked", true);
                $("#protein").prop("checked", false);
                $("#dna-options").show();
                $("#protein-options").hide();
            } else if (data["dna_protein"] == "protein") {
                dnaProtein = "protein";
                $("#protein").prop("checked", true);
                $("#dna").prop("checked", false);
                $("#protein-options").show();
                $("#dna-options").hide();
            }
            $("#selectBSR").val(data["dna_bsr"]);
            $("#selectBF").val(data["dna_bf"]);
            $("#selectDNARHAS").val(data["dna_rhas"]);
            $("#selectAAERM").val(data["protein_aaerm"]);
            $("#selectPMM").val(data["protein_pmm"]);
            $("#selectAAF").val(data["protein_aaf"]);
            $("#selectAARHAS").val(data["protein_rhas"]);
        });
    }

    function load(method, httpData) {
        if (method == "post") {
            $.post("load", httpData, update);
        } else {
            $.get("load", httpData, update);
        }
    }

    function update(data, status, xhr) {
        //alert("Data: " + data + "\nStatus: " + status);
        // TODO work with status?!
        data = JSON.parse(data);
        trees = data;
        number_of_trees = trees.length;
        if (typeof xhr !== "undefined") {
            counter_of_trees += 1;
            set_testing(xhr.getResponseHeader("Testing"));
        }
        if (counter_of_trees > 1) {
            $("#undo-button").prop("disabled", false);
        }
        if (counter_of_trees < number_of_trees) {
            $("#redo-button").prop("disabled", false);
        }
        if (counter_of_trees == number_of_trees) {
            $("#redo-button").prop("disabled", true);
        }
        console.log("Building tree " + counter_of_trees + " of " + number_of_trees);
        draw(eval(trees[counter_of_trees - 1][1]));
        //snapshots(trees);
    }

    function set_testing(testing) {
        if (testing == "enabled") {
            $("#test-snapshots").prop("disabled", false);
            $("#testing-disabled-message").hide();
        } else if (testing == "disabled") {
            $("#test-snapshots").prop("disabled", true);
            $("#testing-disabled-message").show();
        }
    }

    function options(data) {
        $.post("options", data);
        if (typeof trees !== "undefined") {
            load("get", null);
        }
    }

    function description(id, description) {
        $.post("description", {"id": id, "description": description});
    }

    function snapshots(data) {
        $("#no-entries").remove();
        $("#snapshots").empty();
        $("#select-snapshots").empty();
        // TODO $("#snapshots").append('<thead><tr><th scope="col">#</th><th scope="col">JSON</th><th scope="col">Newick</th><th scope="col">DateTime</th></tr></thead>');
        $("#snapshots").append('<thead><tr><th>#</th><th>Description</th><th>Download</th></tr></thead>');
        $("#snapshots").append('<tbody>');
        data.forEach(function(value) {
            text = '<tr>';
            text += '<td><button type="button" class="btn btn-link" id="snapshot-' + value[0] + '">' + value[0] + '</button></td>';
            text += '<td><input type="text" class="form-control" id="snapshot-description-' + value[0] + '" value="' + ((value[2] != null) ? value[2] : "") + '"></td>';
            text += '<td><button type="button" class="btn btn-link" id="snapshot-download-' + value[0] + '"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-download" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path fill-rule="evenodd" d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg></button></td>';
            text += '</tr>';
            $("#snapshots").append(text);
            $("#snapshot-" + value[0]).click(function() {
                snapshotId = $(this).attr("id").split("-")[1];
                draw(eval(trees[snapshotId - 1][1]));
            });
            $("#snapshot-description-" + value[0]).change(function() {
                snapshotId = $(this).attr("id").split("-")[2];
                description(snapshotId, $(this).val());
            });
            $("#snapshot-download-" + value[0]).click(function() {
                snapshotId = $(this).attr("id").split("-")[2];
                download(snapshotId);
            });
            // TODO no-entries option for tests too?!
            $("#select-snapshots").append('<option>' + value[0] + '</option>');
        });
        $("#snapshots").append('</tbody>');
    }

    function tests(data) {
        $("#modalLabel").text("Tests clicked!")
        $("#modalBody").text("Tests are getting calculated!")
        $("#modal").modal("show");
        $.post("tests", data, function(data) {
            data = JSON.parse(data);

            var testData = new Array(10);

            for (var i = 0; i < testData.length; i++) {
                testData[i] = new Array();
            }

            testData[0].push('#');
            testData[1].push('logL');
            testData[2].push('<a href="#" title="deltaL" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="logL difference from the maximal logL in the set">deltaL</a>');
            testData[3].push('<a href="#" title="bp-RELL" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="bootstrap proportion using <a href=\'https://doi.org/10.1007/BF02109483\' target=\'_blank\'>RELL method (Kishino et al. 1990)</a>">bp-RELL</a>');
            testData[4].push('<a href="#" title="p-KH" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="p-value of one sided <a href=\'https://doi.org/10.1007/BF02100115\' target=\'_blank\'>Kishino-Hasegawa test (1989)</a>">p-KH</a>');
            testData[5].push('<a href="#" title="p-SH" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="p-value of <a href=\'https://doi.org/10.1093/oxfordjournals.molbev.a026201\' target=\'_blank\'>Shimodaira-Hasegawa test (2000)</a>">p-SH</a>');
            testData[6].push('<a href="#" title="p-WKH" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="p-value of weighted <a href=\'https://doi.org/10.1007/BF02100115\' target=\'_blank\'>KH</a>">p-WKH</a>');
            testData[7].push('<a href="#" title="p-WSH" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="p-value of weighted <a href=\'https://doi.org/10.1093/oxfordjournals.molbev.a026201\' target=\'_blank\'>SH</a>">p-WSH</a>');
            testData[8].push('<a href="#" title="c-ELW" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="Expected Likelihood Weight <a href=\'https://doi.org/10.1098/rspb.2001.1862\' target=\'_blank\'>(Strimmer & Rambaut 2002)</a>">c-ELW</a>');
            testData[9].push('<a href="#" title="p-AU" data-toggle="popover" data-trigger="focus" data-placement="left" data-html="true" data-content="p-value of <a href=\'https://doi.org/10.1080/10635150290069913\' target=\'_blank\'>approximately unbiased (AU) test (Shimodaira, 2002)</a>">p-AU</a>');

            data.forEach(function(value) {
                testData[0].push(value[0], "");
                testData[1].push(parseFloat(value[1]).toFixed(2), "");
                testData[2].push(parseFloat(value[2]).toFixed(2), "");
                testData[3].push(value[3], value[4]);
                testData[4].push(value[5], value[6]);
                testData[5].push(value[7], value[8]);
                testData[6].push(value[9], value[10]);
                testData[7].push(value[11], value[12]);
                testData[8].push(value[13], value[14]);
                testData[9].push(value[15], value[16]);
            });

            $("#tests").empty();

            for (var i = 0; i < testData.length; i++) {
                if (i == 0) {
                    start = "<thead><tr>";
                    end = "</tr></thead>";
                    first = true;
                } else {
                    start = "<tbody><tr>";
                    end = "</tr></tbody>";
                    first = false;
                }
                $("#tests").append(start);
                for (var j = 0; j < testData[i].length; j++) {
                    if (j == 0 || first) {
                        $("#tests").append('<th>' + testData[i][j] + '</th>');
                    } else {
                        $("#tests").append('<td>' + testData[i][j] + '</td>');
                    }
                }
                $("#tests").append(end);
                $('[data-toggle="popover"]').popover();
            }
        });
    }

    function download(id) {
        window.open("download/" + id);
    }

    function draw(data) {
        xBefore = getTransform("x");
        yBefore = getTransform("y");
        scaleBefore = getTransform("scale");

        $("#logo-main").remove();
        $("#logo-slide").remove();

        if (typeof svg !== "undefined") {
            svg.remove();
        }

        if (typeof minimap !== "undefined") {
            minimap.remove();
        }

        svg = Snap(maxWidth, maxHeight);
        $(svg.node).appendTo($("#mainDiv"));

        extraData = data.pop();

        enableLengths = extraData["enable_lengths"];
        maxLength = extraData["max_length"];
        longestName = extraData["longest_name"];

        let fontSize = '1.375em';
        let strokeWidth = 4;

        longestNameTester = svg.text(0, 0, longestName).attr({
            fontSize: fontSize
        });
        longestNameWidth = Math.ceil(longestNameTester.getBBox().width);
        longestNameTester.remove();

        // TODO instead of checking longest name, we have to check longest combination of line with length and name for each and get longest total line

        amount = data.length;

        offset = 10;
        multiplier = enableLengths ? 10 : 1;
        //scaleX = 200;
        scaleX = 50 * multiplier;
        scaleY = 30;

        svg.remove();
        //svg = Snap(((scaleX * maxLength) + (2.5 * offset) + longestNameWidth), (scaleY * (amount + 1)));
        //$(svg.node).appendTo($("#mainDiv"));
        maxX = (scaleX * maxLength) + (3.5 * offset) + longestNameWidth;
        maxY = scaleY * (amount + 1);
        svg = Snap(maxWidth, maxHeight);
        $(svg.node).appendTo($("#mainDiv"));
        g = svg.g();
        lines = g.g();
        g.add(svg.path("M0,0H" + maxX + "V" + maxY + "H0Z").attr({
            fill: 'none',
            stroke: 'black',
            strokeWidth: 2
        }));

        activate_buttons();

        minimapMaxWidth = $("#tab1").width();
        minimapMaxHeight = $("#tab1").height();
        minimap = Snap(minimapMaxWidth, minimapMaxHeight);
        $(minimap.node).appendTo($("#tab1"));

        minimapOffset = 1;
        minimapMinX = minimapOffset;
        minimapMinY = minimapOffset;

        minimapMaxY = minimapMaxHeight - minimapOffset;
        ratio = maxY / (minimapMaxY - minimapMinY);
        minimapMaxX = maxX / ratio;

        if (minimapMaxX > minimapMaxWidth) {
            minimapMaxX = minimapMaxWidth - minimapOffset;
            ratio = maxX / (minimapMaxX - minimapMinX);
            minimapMaxY = maxY / ratio;
        }

        minimapWindowMaxX = $(window).width() / ratio;
        minimapWindowMaxY = $(window).height() / ratio;

        minimapWindow = minimap.path("M" + minimapMinX + "," + minimapMinY + "H" + minimapWindowMaxX + "V" + minimapWindowMaxY + "H" + minimapMinX + "Z").attr({
            fill: 'lightgray',
            fillOpacity: 0.5,
            stroke: 'black',
            strokeWidth: 1,
            'vector-effect': 'non-scaling-stroke'
        });

        border = minimap.path("M" + minimapMinX + "," + minimapMinY + "H" + minimapMaxX + "V" + minimapMaxY + "H" + minimapMinX + "Z").attr({
            fill: 'transparent',
            stroke: 'black',
            strokeWidth: 1
        });

        border.click(function(event) {
            posX = event.offsetX;
            posY = event.offsetY;
            moveX = posX * ratio;
            moveY = posY * ratio;
            setTransform("translate", -moveX + maxWidth / 2, -moveY + maxHeight / 2);
        });

        // TODO write this nicer
        topBottom = [-5, maxY + 15];
        let topBottomLine;
        topBottom.forEach(function(value) {
            for (var i = 0; i < maxLength * multiplier; i++) {
                topBottomLine = svg.line(10 + scaleX * i / multiplier, value - 10, 10 + scaleX * i / multiplier, value).attr({
                    fill: 'none',
                    stroke: 'black',
                    strokeWidth: 2
                });
                topBottomLine.append(Snap.parse('<title>' + i / multiplier + '</title>'));
                lines.add(topBottomLine);
                // TODO could be put exactly in the middle, now only puts the beginning above the line
                // g.add(svg.text(10 + scaleX * i, value - 20, i + ".0").attr({dominantBaseline: 'middle', fontSize: fontSize}));
            }
            topBottomLine = svg.line(10 + scaleX * maxLength, value - 10, 10 + scaleX * maxLength, value).attr({
                fill: 'none',
                stroke: 'black',
                strokeWidth: 2
            });
            topBottomLine.append(Snap.parse('<title>' + maxLength + '</title>'));
            lines.add(topBottomLine);
            // TODO could be put exactly in the middle, now only puts the beginning above the line
            // g.add(svg.text(10 + scaleX * maxLength, value - 20, maxLength).attr({dominantBaseline: 'middle', fontSize: fontSize}));
            lines.add(svg.line(10, value - 5, 10 + scaleX * maxLength, value - 5).attr({
                fill: 'none',
                stroke: 'black',
                strokeWidth: 2
            }));
        });
        for (var i = 0; i < maxLength * multiplier; i++) {
            topBottomLine = svg.line(10 + scaleX * i / multiplier, topBottom[0], 10 + scaleX * i / multiplier, topBottom[1] - 10).attr({
                fill: 'none',
                stroke: 'black',
                strokeWidth: 2,
                strokeOpacity: 0.125
            });
            topBottomLine.append(Snap.parse('<title>' + i / multiplier + '</title>'));
            lines.add(topBottomLine);
        }
        topBottomLine = svg.line(10 + scaleX * maxLength, topBottom[0], 10 + scaleX * maxLength, topBottom[1] - 10).attr({
            fill: 'none',
            stroke: 'black',
            strokeWidth: 2,
            strokeOpacity: 0.125
        });
        topBottomLine.append(Snap.parse('<title>' + maxLength + '</title>'));
        lines.add(topBottomLine);

        //svg.mousedown(funcMouseDown);
        //svg.mouseup(funcMouseUp);
        //svg.mousemove(funcMouseMove);

        //scaleX = (maxWidth - longestNameWidth - (2.5 * offset)) / maxLength;
        //scaleY = maxHeight / (amount + 1);

        //let paths = [];

        let hoveredPath;
        let hoveredLine;
        let clickedPath;
        let nameText;

        let outgroupButton;
        let outgroupButtonBlock = svg.rect(-50, 0, 40, maxY, 10).attr({
            fill: "#007bff"
        });
        let outgroupButtonText = svg.text(-maxY/2, -30, "Outgroup").attr({ //#+textLength/2 TODO
            dominantBaseline: 'middle',
            fontSize: 25,
            textAnchor: 'middle',
            fill: 'white'
        });
        outgroupButtonText.transform("rotate(270)");
        outgroupButton = svg.g(outgroupButtonBlock, outgroupButtonText);
        outgroupButton.attr({
            display: 'none',
            id: 'outgroupButton'
        });
        outgroupButton.click(function() {
            if (!(typeof clickedPath === "undefined" || (typeof clickedPath === "object" && !clickedPath))) {
                if (counter_of_trees == number_of_trees) {
                    load("get", {
                        'id': clickedPath.attr("data-id")
                    });
                } else {
                    load("get", {
                        'id': clickedPath.attr("data-id"),
                        'current': counter_of_trees
                    });
                }
            } else if (clickedPath.attr("data-parent") != 0) {
                clickedPath.attr({
                    strokeOpacity: ''
                });
                childrenIds = [clickedPath.attr("data-l_child"), clickedPath.attr("data-r_child")];
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
                clickedPath = null;
                toggleOutgroupButton();
            }
        });
        $("#outgroupButton").css("cursor", "pointer");
        g.add(outgroupButton);

        data.forEach(function(item, index, array) {
            if (item["name"] != "None") {
                // TODO draw all texts at the right
                // with path stroke dasharray
                //g.add(svg.text(item["total_length"] * scaleX + (1.5 * offset), (index + 1) * scaleY, item["name"]).attr({dominantBaseline: 'middle', fontSize: fontSize, 'data-id': item["id"]}));
                nameText = svg.text(maxX - offset, (index + 1) * scaleY, item["name"]).attr({
                    dominantBaseline: 'middle',
                    fontSize: fontSize,
                    'data-id': item["id"],
                    textAnchor: 'end'
                });
                g.add(nameText);
                if (item["total_length"] * scaleX + (1.5 * offset) < maxX - (1.5 * offset) - Math.ceil(nameText.getBBox().width) - offset) {
                    g.add(svg.line(item["total_length"] * scaleX + (1.5 * offset), (index + 1) * scaleY, maxX - (1.5 * offset) - Math.ceil(nameText.getBBox().width), (index + 1) * scaleY).attr({
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
                    g.add(svg.text((parseFloat(array[parent]["total_length"]) + (item["length"] / 2)) * scaleX, (index + 1) * scaleY, item["bootstrap"]).attr({
                        dominantBaseline: 'baseline',
                        fontSize: 0.5 * fontSize,
                        'data-id': item["id"]
                    }));
                    // TODO data-id added graying out of child bootstraps but not selected bootstrap
                }

                l_child = array.findIndex((elem)=>elem.id == item["l_child"]);
                r_child = array.findIndex((elem)=>elem.id == item["r_child"]);

                mX = (item["total_length"] * scaleX) + offset;
                mYLeft = (index + 1) * scaleY - strokeWidth;
                mYRight = (index + 1) * scaleY + strokeWidth;

                if (item["id"] == 0) {
                    mYLeft += strokeWidth / 2;
                    mYRight -= strokeWidth / 2;
                }

                vLeft = (l_child + 1) * scaleY;
                vRight = (r_child + 1) * scaleY;
                hLeft = array[l_child]["total_length"] * scaleX + offset;
                hRight = array[r_child]["total_length"] * scaleX + offset;

                left = svg.path("M" + mX + "," + mYLeft + "V" + vLeft + "H" + hLeft).attr({
                    "data-id": array[l_child]["id"],
                    "data-parent": item["id"]
                });
                right = svg.path("M" + mX + "," + mYRight + "V" + vRight + "H" + hRight).attr({
                    "data-id": array[r_child]["id"],
                    "data-parent": item["id"]
                });
                g.add(left, right);

                mXMinimap = minimapMinX + mX / ratio;
                mYLeftMinimap = minimapMinY + mYLeft / ratio;
                vLeftMinimap = minimapMinY + vLeft / ratio;
                hLeftMinimap = minimapMinX + hLeft / ratio;
                mYRightMinimap = minimapMinY + mYRight / ratio;
                vRightMinimap = minimapMinY + vRight / ratio;
                hRightMinimap = minimapMinX + hRight / ratio;
                minimapLeft = minimap.path("M" + mXMinimap + "," + mYLeftMinimap + "V" + vLeftMinimap + "H" + hLeftMinimap);
                minimapRight = minimap.path("M" + mXMinimap + "," + mYRightMinimap + "V" + vRightMinimap + "H" + hRightMinimap);

                minimapPaths = [minimapLeft, minimapRight];

                minimapPaths.forEach(function(itemMinimapPath, indexMinimapPath, arrayMinimapPath) {
                    itemMinimapPath.attr({
                        fill: 'none',
                        stroke: 'black',
                        strokeWidth: strokeWidth / ratio,
                        strokeLinecap: 'square'
                    });
                });

                if (array[l_child]["bootstrap"] != "") {
                    left.append(Snap.parse('<title>' + array[l_child]["bootstrap"] + '</title>'));
                }
                if (array[r_child]["bootstrap"] != "") {
                    right.append(Snap.parse('<title>' + array[r_child]["bootstrap"] + '</title>'));
                }

                if (("l_child" in array[l_child]) && ("r_child" in array[l_child])) {
                    left.attr({
                        "data-l_child": array[l_child]["l_child"],
                        "data-r_child": array[l_child]["r_child"]
                    });
                }
                if (("l_child" in array[r_child]) && ("r_child" in array[r_child])) {
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
                        // Select first path
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
                            toggleOutgroupButton();
                        // Both paths are the same
                        } else if ((clickedPath == itemPath) ||
                        // Both paths are neighbors
                        (clickedPath.attr("data-parent") == itemPath.attr("data-parent")) ||
                        // Second path is the first one's parent
                        (clickedPath.attr("data-parent") == itemPath.attr("data-id"))) {
                            hoveredPath.remove();
                            clickedPath.attr({
                                strokeOpacity: ''
                            });
                            childrenIds = [clickedPath.attr("data-l_child"), clickedPath.attr("data-r_child")];
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
                            clickedPath = null;
                            toggleOutgroupButton();
                        } else {
                            if (counter_of_trees == number_of_trees) {
                                load("get", {
                                    'from': clickedPath.attr("data-id"),
                                    'to': itemPath.attr("data-id")
                                });
                            } else {
                                load("get", {
                                    'from': clickedPath.attr("data-id"),
                                    'to': itemPath.attr("data-id"),
                                    'current': counter_of_trees
                                });
                            }
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

        if (xBefore === "undefined") {
            xBefore = 20;
        }

        if (yBefore === "undefined") {
            yBefore = 20;
        }

        if (scaleBefore === "undefined") {
            setTransform("translate", xBefore, yBefore);
        } else {
            setTransform("scale", scaleBefore, xBefore, yBefore);
        }

        // TODO think of the boundaries!
        var startX, startY;
        let move;
        let step = 0.1;

        function funcMouseDown(event) {
            startX = event.clientX;
            startY = event.clientY;
            move = true;
            // TODO only when existing?
            $(svg.node).css("cursor", "move");
        }

        function funcMouseUp(event) {
            move = false;
            // TODO only when existing?
            $(svg.node).removeAttr("style");
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
            currentX = getTransform("x");
            currentY = getTransform("y");
            currentScale = getTransform("scale");

            posX = event.originalEvent.clientX;
            posY = event.originalEvent.clientY;

            if (posX == 0) {
                posX = 1;
            }

            if (posY == 0) {
                posY = 1;
            }

            if (event.originalEvent.deltaY < 0) {
                newScale = currentScale + step;
            } else {
                newScale = currentScale - step;
            }

            moveX = currentX + (currentX - posX) * (newScale - currentScale);
            moveY = currentY + (currentY - posY) * (newScale - currentScale);

            setTransform("scale", newScale, moveX, moveY);
        }

        function setTransform() {
            if (typeof g === "undefined") {
                return;
            }
            originalTranslateX = getTransform("x");
            originalTranslateY = getTransform("y");
            originalScale = getTransform("scale");

            if (arguments[0] == "translate") {
                scale = originalScale;
                translateX = arguments[1];
                translateY = arguments[2];
            } else if (arguments[0] == "scale") {
                scale = arguments[1];
                translateX = arguments[2];
                translateY = arguments[3];

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
            // TODO
            minimapWindow.transform("translate(" + -translateX / ratio + " " + -translateY / ratio + ") scale(" + scale + " " + scale + ")");
        }

        function getTransform() {
            if (typeof g === "undefined") {
                return;
            }
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

        function toggleOutgroupButton() {
            if (outgroupButton.attr("display") == "none") {
                outgroupButton.attr({display: "inline"});
            } else if (outgroupButton.attr("display") == "inline") {
                outgroupButton.attr({display: "none"});
            }
        }

        function activate_buttons() {
            if (!(buttons_activated)) {
                $("#undo-button").show();
                $("#redo-button").show();
                $("#zoom-in-button").show();
                $("#zoom-out-button").show();
                $("#search").css("display", "flex");

                $("#undo-button").click(function (event) {
                    undo();
                });

                $("#redo-button").click(function (event) {
                    redo();
                });

                $("#zoom-in-button").click(function (event) {
                    setTransform("scale", getTransform("scale") + step, getTransform("x"), getTransform("y"));
                });

                $("#zoom-out-button").click(function (event) {
                    setTransform("scale", getTransform("scale") - step, getTransform("x"), getTransform("y"));
                });

                $("#search-button").click(function (event) {
                    search($("#search-text").val());
                });

                $('#search-text').keypress(function (event) {
                    if (event.which == '13') {
                        search($("#search-text").val());
                    }
                });
                buttons_activated = true;
            }
        }

        function search(value) {
            data.some(function(item, index, array) {
                if (item.name != "None" && item.name.toLowerCase().includes(value.toLowerCase())) {
                    found = svg.select("text[data-id='" + item.id + "']");
                    if (found) {
                        found.attr('fill', 'red');
                        setTimeout(function() {
                            found.attr('fill', null);
                        }, 2000);
                    }
                    setTransform("translate", -(maxX - offset) + maxWidth / 2, -((index + 1) * scaleY) + maxHeight / 2);
                    return true;
                }
            });
        }

        function undo() {
            if (counter_of_trees > 1) {
                counter_of_trees -= 1;
            }
            if (counter_of_trees == 1) {
                $("#undo-button").prop("disabled", true);
            }
            update(JSON.stringify(trees));
        }

        function redo() {
            if (counter_of_trees < number_of_trees) {
                counter_of_trees += 1;
            }
            if (counter_of_trees == number_of_trees) {
                $("#redo-button").prop("disabled", true);
            }
            update(JSON.stringify(trees));
        }
    }

    //TODO this can be simplified!

    var onOffBtn1 = "off";
    var onOffBtn2 = "off";
    var onOffBtn3 = "off";
    var onOffBtn4 = "off";
    var exnum = 0;
    var num = 0;

    $("#btnClose").click(function() {
        onOffBtn1 = "off";
        onOffBtn2 = "off";
        onOffBtn3 = "off";
        onOffBtn4 = "off";
        exnum = 0;
        num = 0;
        $("#tab1").hide("fast");
        $("#tab2").hide("fast");
        $("#tab3").hide("fast");
        $("#tab4").hide("fast");
    });

    $("#btn1").click(function() {
        num = 1;
        switch (onOffBtn1) {
        case "off":
            {
                $("#tab" + exnum).hide("fast");
                $("#tab" + num).show("fast");
                onOffBtn4 = "off";
                onOffBtn3 = "off";
                onOffBtn2 = "off";
                onOffBtn1 = "on";
                exnum = 1;
                break;
            }
        case "on":
            {
                $("#tab" + num).hide("fast");
                $("#tab" + exnum).hide("fast");
                onOffBtn4 = "off";
                onOffBtn3 = "off";
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
                onOffBtn4 = "off";
                onOffBtn3 = "off";
                onOffBtn2 = "on";
                onOffBtn1 = "off";
                exnum = 2;
                break;
            }
        case "on":
            {
                $("#tab" + num).hide("fast");
                $("#tab" + exnum).hide("fast");
                onOffBtn4 = "off";
                onOffBtn3 = "off";
                onOffBtn2 = "off";
                onOffBtn1 = "off";
                break;
            }
        }
    });

    $("#btn3").click(function() {
        num = 3;
        switch (onOffBtn3) {
        case "off":
            {
                $("#tab" + exnum).hide("fast");
                $("#tab" + num).show("fast");
                onOffBtn4 = "off";
                onOffBtn3 = "on";
                onOffBtn2 = "off";
                onOffBtn1 = "off";
                exnum = 3;
                break;
            }
        case "on":
            {
                $("#tab" + num).hide("fast");
                $("#tab" + exnum).hide("fast");
                onOffBtn4 = "off";
                onOffBtn3 = "off";
                onOffBtn2 = "off";
                onOffBtn1 = "off";
                break;
            }
        }
    });

    $("#btn4").click(function() {
        num = 4;
        switch (onOffBtn4) {
        case "off":
            {
                $("#tab" + exnum).hide("fast");
                $("#tab" + num).show("fast");
                onOffBtn4 = "on";
                onOffBtn3 = "off";
                onOffBtn2 = "off";
                onOffBtn1 = "off";
                exnum = 4;
                break;
            }
        case "on":
            {
                $("#tab" + num).hide("fast");
                $("#tab" + exnum).hide("fast");
                onOffBtn4 = "off";
                onOffBtn3 = "off";
                onOffBtn2 = "off";
                onOffBtn1 = "off";
                break;
            }
        }
    });

    $("#btn2").click();

});

/*
//TODO
$(window).resize(function() {
    svg.size($(window).width(), $(window).height());
});*/