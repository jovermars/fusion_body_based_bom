# Author-Jelle Overmars
# Description-Extracts the BOM based on bodies instead of components

import adsk.core, adsk.fusion, adsk.cam, traceback

delimiter = "\t"


def exportHtml(bom):
    html = (
        "<table>"
        + "<tr><th>Component</th><th>Body</th><th>Y</th><th>X</th><th>Z</th><th>Manufactured</th></tr>"
    )
    for item in bom:
        html += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>".format(
            item["componentName"],
            item["bodyName"],
            item["bodyY"],
            item["bodyX"],
            item["bodyZ"],
            item["manufactured"],
        )
    html += "</table>"
    return html


def run(context):
    ui = None
    app = adsk.core.Application.get()
    ui = app.userInterface

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    if not design:
        ui.messageBox("The DESIGN workspace must be active when running this script.")
        return

    # Get all occurrences in the root component of the active design
    root = design.activeComponent
    occs = root.allOccurrences

    # Gather information about each unique component
    unitLength = design.unitsManager.defaultLengthUnits

    bom = []
    for occ in occs:
        component = occ.component
        bodies = component.bRepBodies
        for body in bodies:
            bodyDimensions = sorted(
                body.boundingBox.minPoint.vectorTo(body.boundingBox.maxPoint)
                .asPoint()
                .asArray()
            )

            formx = product.unitsManager.formatInternalValue(
                bodyDimensions[1], unitLength, False
            )
            formy = product.unitsManager.formatInternalValue(
                bodyDimensions[2], unitLength, False
            )
            formz = product.unitsManager.formatInternalValue(
                bodyDimensions[0], unitLength, False
            )

            # alwasy have y the biggest value
            if formx > formy:
                tempx = formx
                formx = formy
                formy = tempx

            manufactured = body.name.find("✓")

            bom.append(
                {
                    "componentName": component.name,
                    "bodyName": body.name,
                    "bodyX": formx,
                    "bodyY": formy,
                    "bodyZ": formz,
                    "manufactured": manufactured > -1,
                }
            )

    msg = exportHtml(bom)
    ui.messageBox(msg, "Bill Of Body Materials")
