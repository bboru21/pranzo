<%inherit file="base.html" />

<%block name="header">
    <h1>D.C. Food Trucks</h1>
</%block>

<!--
<form id="search" autocomplete="off">
    <label for="searchName">Search Vendor Name</label>
    <input type="text" id="searchName" placeholder="Search Vendor Name" />

    <label for="searchSitePermit">Search Site Permit</label>
    <input type="text" id="searchSitePermit" placeholder="Search Vendor Site Permit" />
</form>
-->

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Site Permit</th>
            <th>Alias</th>
        </tr>
    </thead>
    <tbody>
        % for vendor in vendors:
            <tr id="${vendor['id']}">
                <td>${vendor['name']}</td>
                <td>${vendor['site_permit']}</td>
                <td>${vendor['alias']}</td>
            </tr>
        % endfor
    </tbody>
</table>

<script id="vendorsData" type="application/json">
{
    "vendors": [
        % for vendor in vendors:
            {
                "id": ${vendor['id']},
                "name": "${vendor['name']}",
                "sitePermit": "${vendor['site_permit']}",
                "alias": "${vendor['alias']}"
            }
            % if not loop.last:
                ,
            % endif
        % endfor
    ]
}
</script>

<div class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        <form>

            <label for="vendorName">
                Name:
            </label>
            <input type="text" id="vendorName" disabled />

            <label for="vendorSitePermit">
                Site&nbsp;Permit:
            </label>
            <input type="text" id="vendorSitePermit" disabled />

            <label for="vendorAlias">
                Alias:
            </label>
            <input type="text" id="vendorAlias" placeholder="Enter Alias Here" />

            <input type="hidden" id="vendorId" />
            <input type="submit" id="submit" value="Update Vendor" />
        </form>
    </div>
</div>

