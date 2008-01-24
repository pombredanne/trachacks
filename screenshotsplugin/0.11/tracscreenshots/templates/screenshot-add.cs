<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:xi="http://www.w3.org/2001/XInclude" xmlns:py="http://genshi.edgewall.org/">
  <xi:include href="layout.html"/>
  <head>
    <title>Screenshots</title>
  </head>

  <body>
    <div id="content" class="screenshots">
      <div class="title">
        <h1>${screenshots.title}</h1>
      </div>

      <form class="add_form" method="post" enctype="multipart/form-data" action="${href.screenshots()}">
        <fieldset>
          <legend>
            ${(req.args.action == 'add') and 'Add Screenshot:' or 'Edit Screenshot'}
          </legend>
          <div class="field">
            <label for="name">Name:</label><br/>
            <input type="text" id="name" name="name" value="${(req.args.action == 'edit') and screenshots.screenshot.name or ''}"/><br/>
          </div>
          <div class="field">
            <label for="description">Description:</label><br/>
            <input type="text" id="description" name="description" value="${(req.args.action == 'edit') and screenshots.screenshot.description or ''}"/><br/>
          </div>
          <div py:if="req.args.action == 'add'" class="field">
            <label for="image">Image File:</label><br/>
            <input type="file" id="image" name="image" value=""/><br/>
          </div>
          <div class="field">
            <label for="tags">Additional tags:</label><br/>
            <input type="text" id="tags" name="tags" value="${(req.args.action == 'edit') and screenshots.screenshot.tags or ''}"/><br/>
          </div>
          <div class="field">
            <label for="components">Components:</label><br/>
            <select id="components" name="components" multiple="on">
              <py:for each="component in screenshots.components">
                <py:choose>
                  <option py:when="(req.args.action == 'edit') and (component.name in screenshots.screenshot.components)" value="${component.name}" selected="selected">${component.name}</option>
                  <option py:otherwise="" value="${component.name}">${component.name}</option>
                </py:choose>
              </py:for>
            </select><br/>
          </div>
          <div class="field">
            <label for="versions">Versions:</label><br/>
            <select id="versions" name="versions" multiple="on">
              <py:for each="version in screenshots.versions">
                <py:choose>
                  <option py:when="(req.args.action == 'edit') and (version.name in screenshots.screenshot.versions)" value="${version.name}" selected="selected">${version.name}</option>
                  <option py:otherwise="" value="${version.name}">${version.name}</option>
                </py:choose>
              </py:for>
            </select><br/>
          </div>
          <div class="buttons">
            <input type="submit" name="submit" value="Submit"/>
            <input type="button" name="cancel" value="Cancel" onclick="history.back()"/>
            <input type="hidden" name="id" value="${(req.args.action == 'edit') and screenshots.screenshot.id or ''}"/>
            <input type="hidden" name="index" value="${screenshots.index}"/>
            <input type="hidden" name="action" value="${(req.args.action == 'add') and 'post-add' or 'post-edit'}"/>
          </div>
        </fieldset>
      </form>
    </div>
  </body>
</html>