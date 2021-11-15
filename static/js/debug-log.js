var wID = "iDemo" + new Date().getTime();

iWin.init({
  onSetTitle: function (wID, obj, title) {
    obj.innerHTML = "<span>[X]</span><span>" + title + "</span>";

    // Capture phase second
    iWin.addEvent(
      iWin.win[wID].obj.children[0].children[0],
      "press",
      function (e) {
        var evt = e || window.event;
        evt.preventDefault();
        iWin.win[wID].onClose(wID, e);
        e.stopPropagation ? e.stopPropagation() : (e.cancelBubble = true);
      },
      true
    );
  },
});

iWin.create(
  {
    title: "Debug Log",
    onClose: function () {
      iWin.destroy(wID);
    },
  },
  wID
);

iWin.setContent("<div class=consoleContainer></div>", wID);
iWin.setContentDimensions({width:840, height:220}, wID);
iWin.setPosition(60, window.innerWidth / 2 - 20, wID);

iWin.show(wID);

debug = $(".consoleContainer").console({ msgDirection: "up" });
