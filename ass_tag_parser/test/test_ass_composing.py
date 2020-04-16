import pytest

from ass_tag_parser import *


@pytest.mark.parametrize(
    "source_blocks,expected_line",
    [
        ([], ""),
        ([AssText("test")], r"test"),
        (
            [AssTagListOpening(), AssTagListEnding()],
            "",  # autoinsert overrides {}
        ),
        ([AssTagComment("asdasd")], r"{asdasd}"),
        (
            [
                AssTagDraw(
                    scale=2,
                    path=[AssDrawCmdMove(AssDrawPoint(3, 4), close=True)],
                )
            ],
            r"{\p2}m 3 4{\p0}",
        ),
        (
            [
                AssTagAlignment(5, legacy=False),
                AssTagAlignment(5, legacy=True),
            ],
            r"{\an5\a6}",
        ),
        (
            [
                AssTagListOpening(),
                AssTagAlignment(5, legacy=False),
                AssTagListEnding(),
                AssTagListOpening(),
                AssTagAlignment(5, legacy=False),
                AssTagListEnding(),
            ],
            r"{\an5\an5}",  # autoinsert overrides {}
        ),
        (
            [
                AssText("abc def"),
                AssTagAlignment(5, legacy=False),
                AssText("ghi jkl"),
                AssTagAlignment(5, legacy=False),
                AssText("123 456"),
            ],
            r"abc def{\an5}ghi jkl{\an5}123 456",
        ),
        (
            [
                AssText("I am "),
                AssTagBold(enabled=True),
                AssText("not"),
                AssTagBold(enabled=False),
                AssText(" amused."),
            ],
            r"I am {\b1}not{\b0} amused.",
        ),
        (
            [
                AssTagBold(weight=100),
                AssText("How "),
                AssTagBold(weight=300),
                AssText("bold "),
                AssTagBold(weight=500),
                AssText("can "),
                AssTagBold(weight=700),
                AssText("you "),
                AssTagBold(weight=900),
                AssText("get?"),
            ],
            r"{\b100}How {\b300}bold {\b500}can {\b700}you {\b900}get?",
        ),
        (
            [
                AssText(r"-Hey\N"),
                AssTagResetStyle(style="Alternate"),
                AssText(r"-Huh?\N"),
                AssTagResetStyle(style=None),
                AssText("-Who are you?"),
            ],
            r"-Hey\N{\rAlternate}-Huh?\N{\r}-Who are you?",
        ),
        (
            [
                AssTagColor(0, 0, 255, 1),
                AssTagAnimation(tags=[AssTagColor(255, 0, 0, 1)]),
                AssText("Hello!"),
            ],
            r"{\1c&HFF0000&\t(\1c&H0000FF&)}Hello!",
        ),
        (
            [
                AssTagAlignment(5, legacy=False),
                AssTagAnimation(
                    [AssTagZRotation(angle=3600)],
                    time1=0,
                    time2=5000,
                    acceleration=None,
                ),
                AssText("Wheee"),
            ],
            r"{\an5\t(0,5000,\frz3600)}Wheee",
        ),
        (
            [
                AssTagAlignment(5, legacy=False),
                AssTagAnimation(
                    [AssTagZRotation(angle=3600)],
                    time1=0,
                    time2=5000,
                    acceleration=0.5,
                ),
                AssText("Wheee"),
            ],
            r"{\an5\t(0,5000,0.5,\frz3600)}Wheee",
        ),
        (
            [
                AssTagAlignment(5, legacy=False),
                AssTagFontXScale(0),
                AssTagFontYScale(0),
                AssTagAnimation(
                    [AssTagFontXScale(100), AssTagFontYScale(100)],
                    time1=0,
                    time2=500,
                    acceleration=None,
                ),
                AssText("Boo!"),
            ],
            r"{\an5\fscx0\fscy0\t(0,500,\fscx100\fscy100)}Boo!",
        ),
        (
            [AssTagComment("comment"), AssTagBold(enabled=True)],
            r"{comment\b1}",
        ),
        (
            [AssTagBold(enabled=True), AssTagComment(text="comment")],
            r"{\b1comment}",
        ),
        (
            [AssTagAlpha(0xFF, 2), AssTagComment("comment")],
            r"{\2a&HFF&comment}",
        ),
        ([AssTagBlurEdges(times=2), AssTagComment(".2")], r"{\be2.2}"),
        ([AssTagFontSize(size=5), AssTagComment(text=".4")], r"{\fs5.4}"),
        ([AssTagKaraoke(duration=505, karaoke_type=1)], r"{\k50.5}"),
        ([AssTagKaraoke(duration=505, karaoke_type=2)], r"{\K50.5}"),
        ([AssTagKaraoke(duration=505, karaoke_type=3)], r"{\kf50.5}"),
        ([AssTagKaraoke(duration=505, karaoke_type=4)], r"{\ko50.5}"),
        (
            [AssTagKaraoke(duration=500, karaoke_type=1), AssTagComment(".5")],
            r"{\k50.5}",
        ),
        (
            [AssTagKaraoke(duration=500, karaoke_type=2), AssTagComment(".5")],
            r"{\K50.5}",
        ),
        (
            [AssTagKaraoke(duration=500, karaoke_type=3), AssTagComment(".5")],
            r"{\kf50.5}",
        ),
        (
            [AssTagKaraoke(duration=500, karaoke_type=4), AssTagComment(".5")],
            r"{\ko50.5}",
        ),
    ],
)
def test_composing_valid_ass_line(
    source_blocks: T.List[AssItem], expected_line: str
) -> None:
    assert expected_line == compose_ass(source_blocks)


@pytest.mark.parametrize(
    "source_tag,expected_line",
    [
        (AssTagItalic(enabled=True), r"{\i1}"),
        (AssTagItalic(enabled=False), r"{\i0}"),
        (AssTagItalic(enabled=None), r"{\i}"),
        (AssTagBold(weight=300), r"{\b300}"),
        (AssTagBold(enabled=True), r"{\b1}"),
        (AssTagBold(enabled=False), r"{\b0}"),
        (AssTagBold(enabled=None), r"{\b}"),
        (AssTagUnderline(enabled=True), r"{\u1}"),
        (AssTagUnderline(enabled=False), r"{\u0}"),
        (AssTagUnderline(enabled=None), r"{\u}"),
        (AssTagStrikeout(enabled=True), r"{\s1}"),
        (AssTagStrikeout(enabled=False), r"{\s0}"),
        (AssTagStrikeout(enabled=None), r"{\s}"),
        (AssTagBorder(size=0), r"{\bord0}"),
        (AssTagXBorder(size=0), r"{\xbord0}"),
        (AssTagYBorder(size=0), r"{\ybord0}"),
        (AssTagBorder(size=1.0), r"{\bord1}"),
        (AssTagXBorder(size=1.0), r"{\xbord1}"),
        (AssTagYBorder(size=1.0), r"{\ybord1}"),
        (AssTagBorder(size=4.4), r"{\bord4.4}"),
        (AssTagXBorder(size=4.4), r"{\xbord4.4}"),
        (AssTagYBorder(size=4.4), r"{\ybord4.4}"),
        (AssTagBorder(size=None), r"{\bord}"),
        (AssTagXBorder(size=None), r"{\xbord}"),
        (AssTagYBorder(size=None), r"{\ybord}"),
        (AssTagShadow(size=0), r"{\shad0}"),
        (AssTagXShadow(size=0), r"{\xshad0}"),
        (AssTagYShadow(size=0), r"{\yshad0}"),
        (AssTagShadow(size=1.0), r"{\shad1}"),
        (AssTagXShadow(size=1.0), r"{\xshad1}"),
        (AssTagYShadow(size=1.0), r"{\yshad1}"),
        (AssTagShadow(size=4.4), r"{\shad4.4}"),
        (AssTagXShadow(size=4.4), r"{\xshad4.4}"),
        (AssTagYShadow(size=4.4), r"{\yshad4.4}"),
        (AssTagShadow(size=None), r"{\shad}"),
        (AssTagXShadow(size=None), r"{\xshad}"),
        (AssTagYShadow(size=None), r"{\yshad}"),
        (AssTagBlurEdges(times=2), r"{\be2}"),
        (AssTagBlurEdges(times=None), r"{\be}"),
        (AssTagBlurEdgesGauss(weight=1.0), r"{\blur1}"),
        (AssTagBlurEdgesGauss(weight=4.4), r"{\blur4.4}"),
        (AssTagBlurEdgesGauss(weight=None), r"{\blur}"),
        (AssTagFontName(name=None), r"{\fn}"),
        (AssTagFontName(name="Arial"), r"{\fnArial}"),
        (AssTagFontName(name="Comic Sans"), r"{\fnComic Sans}"),
        (AssTagFontEncoding(encoding=5), r"{\fe5}"),
        (AssTagFontEncoding(encoding=None), r"{\fe}"),
        (AssTagFontSize(size=15), r"{\fs15}"),
        (AssTagFontSize(size=None), r"{\fs}"),
        (AssTagFontXScale(scale=1.0), r"{\fscx1}"),
        (AssTagFontYScale(scale=1.0), r"{\fscy1}"),
        (AssTagFontXScale(scale=5.5), r"{\fscx5.5}"),
        (AssTagFontYScale(scale=5.5), r"{\fscy5.5}"),
        (AssTagFontXScale(scale=None), r"{\fscx}"),
        (AssTagFontYScale(scale=None), r"{\fscy}"),
        (AssTagLetterSpacing(spacing=1), r"{\fsp1}"),
        (AssTagLetterSpacing(spacing=5.5), r"{\fsp5.5}"),
        (AssTagLetterSpacing(spacing=-5.5), r"{\fsp-5.5}"),
        (AssTagLetterSpacing(spacing=None), r"{\fsp}"),
        (AssTagXRotation(angle=1.0), r"{\frx1}"),
        (AssTagXRotation(angle=5.5), r"{\frx5.5}"),
        (AssTagXRotation(angle=-5.5), r"{\frx-5.5}"),
        (AssTagXRotation(angle=None), r"{\frx}"),
        (AssTagYRotation(angle=1.0), r"{\fry1}"),
        (AssTagYRotation(angle=5.5), r"{\fry5.5}"),
        (AssTagYRotation(angle=-5.5), r"{\fry-5.5}"),
        (AssTagYRotation(angle=None), r"{\fry}"),
        (AssTagZRotation(angle=1.0), r"{\frz1}"),
        (AssTagZRotation(angle=1.0, short=True), r"{\fr1}"),
        (AssTagZRotation(angle=5.5), r"{\frz5.5}"),
        (AssTagZRotation(angle=-5.5), r"{\frz-5.5}"),
        (AssTagZRotation(angle=None), r"{\frz}"),
        (AssTagRotationOrigin(x=1, y=2), r"{\org(1,2)}"),
        (AssTagRotationOrigin(x=-1, y=-2), r"{\org(-1,-2)}"),
        (AssTagRotationOrigin(x=1.0, y=2.0), r"{\org(1,2)}"),
        (AssTagRotationOrigin(x=1.1, y=2.2), r"{\org(1.1,2.2)}"),
        (AssTagXShear(value=1.0), r"{\fax1}"),
        (AssTagYShear(value=1.0), r"{\fay1}"),
        (AssTagXShear(value=-1.5), r"{\fax-1.5}"),
        (AssTagYShear(value=-1.5), r"{\fay-1.5}"),
        (AssTagXShear(value=None), r"{\fax}"),
        (AssTagYShear(value=None), r"{\fay}"),
        (AssTagColor(0x56, 0x34, 0x12, 1, short=True), r"{\c&H123456&}"),
        (AssTagColor(0x56, 0x34, 0x12, 1), r"{\1c&H123456&}"),
        (AssTagColor(0x56, 0x34, 0x12, 2), r"{\2c&H123456&}"),
        (AssTagColor(0x56, 0x34, 0x12, 3), r"{\3c&H123456&}"),
        (AssTagColor(0x56, 0x34, 0x12, 4), r"{\4c&H123456&}"),
        (AssTagColor(None, None, None, 1, short=True), r"{\c}"),
        (AssTagColor(None, None, None, 1), r"{\1c}"),
        (AssTagColor(None, None, None, 2), r"{\2c}"),
        (AssTagColor(None, None, None, 3), r"{\3c}"),
        (AssTagColor(None, None, None, 4), r"{\4c}"),
        (AssTagAlpha(0x12, 0), r"{\alpha&H12&}"),
        (AssTagAlpha(0x12, 1), r"{\1a&H12&}"),
        (AssTagAlpha(0x12, 2), r"{\2a&H12&}"),
        (AssTagAlpha(0x12, 3), r"{\3a&H12&}"),
        (AssTagAlpha(0x12, 4), r"{\4a&H12&}"),
        (AssTagAlpha(None, 0), r"{\alpha}"),
        (AssTagAlpha(None, 1), r"{\1a}"),
        (AssTagAlpha(None, 2), r"{\2a}"),
        (AssTagAlpha(None, 3), r"{\3a}"),
        (AssTagAlpha(None, 4), r"{\4a}"),
        (AssTagKaraoke(duration=500, karaoke_type=1), r"{\k50}"),
        (AssTagKaraoke(duration=500, karaoke_type=2), r"{\K50}"),
        (AssTagKaraoke(duration=500, karaoke_type=3), r"{\kf50}"),
        (AssTagKaraoke(duration=500, karaoke_type=4), r"{\ko50}"),
        (AssTagAlignment(5, legacy=False), r"{\an5}"),
        (AssTagAlignment(None, legacy=False), r"{\an}"),
        (AssTagAlignment(None, legacy=True), r"{\a}"),
        (AssTagAlignment(1, legacy=True), r"{\a1}"),
        (AssTagAlignment(2, legacy=True), r"{\a2}"),
        (AssTagAlignment(3, legacy=True), r"{\a3}"),
        (AssTagAlignment(4, legacy=True), r"{\a5}"),
        (AssTagAlignment(5, legacy=True), r"{\a6}"),
        (AssTagAlignment(6, legacy=True), r"{\a7}"),
        (AssTagAlignment(7, legacy=True), r"{\a9}"),
        (AssTagAlignment(8, legacy=True), r"{\a10}"),
        (AssTagAlignment(9, legacy=True), r"{\a11}"),
        (AssTagWrapStyle(style=0), r"{\q0}"),
        (AssTagWrapStyle(style=1), r"{\q1}"),
        (AssTagWrapStyle(style=2), r"{\q2}"),
        (AssTagWrapStyle(style=3), r"{\q3}"),
        (AssTagResetStyle(style=None), r"{\r}"),
        (AssTagResetStyle(style="Some style"), r"{\rSome style}"),
        (AssTagDraw(scale=1, path=[]), r"{\p1}{\p0}"),
        (AssTagBaselineOffset(y=1.0), r"{\pbo1}"),
        (AssTagBaselineOffset(y=1.1), r"{\pbo1.1}"),
        (AssTagBaselineOffset(y=-50), r"{\pbo-50}"),
        (AssTagPosition(x=1, y=2), r"{\pos(1,2)}"),
        (AssTagPosition(x=1.0, y=2.0), r"{\pos(1,2)}"),
        (AssTagPosition(x=1.1, y=2.2), r"{\pos(1.1,2.2)}"),
        (
            AssTagMove(x1=1, y1=2, x2=3, y2=4, time1=None, time2=None),
            r"{\move(1,2,3,4)}",
        ),
        (
            AssTagMove(x1=1.0, y1=2.0, x2=3.0, y2=4.0, time1=5.0, time2=6.0),
            r"{\move(1,2,3,4,5,6)}",
        ),
        (
            AssTagMove(x1=1.1, y1=2.2, x2=3.3, y2=4.4, time1=5.5, time2=6.6),
            r"{\move(1.1,2.2,3.3,4.4,5.5,6.6)}",
        ),
        (
            AssTagMove(x1=1, y1=2, x2=3, y2=4, time1=100, time2=300),
            r"{\move(1,2,3,4,100,300)}",
        ),
        (AssTagFade(time1=100, time2=200), r"{\fad(100,200)}"),
        (AssTagFade(time1=1.0, time2=2.0), r"{\fad(1,2)}"),
        (AssTagFade(time1=1.1, time2=2.2), r"{\fad(1.1,2.2)}"),
        (
            AssTagFadeComplex(
                alpha1=1,
                alpha2=2,
                alpha3=3,
                time1=4.0,
                time2=5.0,
                time3=6.0,
                time4=7.0,
            ),
            r"{\fade(1,2,3,4,5,6,7)}",
        ),
        (
            AssTagFadeComplex(
                alpha1=1,
                alpha2=2,
                alpha3=3,
                time1=4.4,
                time2=5.5,
                time3=6.6,
                time4=7.7,
            ),
            r"{\fade(1,2,3,4.4,5.5,6.6,7.7)}",
        ),
        (
            AssTagFadeComplex(
                alpha1=1,
                alpha2=2,
                alpha3=3,
                time1=4,
                time2=5,
                time3=6,
                time4=7,
            ),
            r"{\fade(1,2,3,4,5,6,7)}",
        ),
        (
            AssTagAnimation([], time1=1.0, time2=2.0, acceleration=3.0),
            r"{\t(1,2,3,)}",
        ),
        (
            AssTagAnimation(
                [AssTagBlurEdges(5), AssTagFontSize(40)],
                time1=1.1,
                time2=2.2,
                acceleration=3.3,
            ),
            r"{\t(1.1,2.2,3.3,\be5\fs40)}",
        ),
        (AssTagAnimation([], acceleration=1.0), r"{\t(1,)}"),
        (
            AssTagAnimation(
                [AssTagBlurEdges(5), AssTagFontSize(40)], acceleration=1.2
            ),
            r"{\t(1.2,\be5\fs40)}",
        ),
        (
            AssTagAnimation(
                [AssTagBlurEdges(5), AssTagFontSize(40)], time1=50, time2=100
            ),
            r"{\t(50,100,\be5\fs40)}",
        ),
        (
            AssTagAnimation([AssTagBlurEdges(5), AssTagFontSize(40)]),
            r"{\t(\be5\fs40)}",
        ),
        (
            AssTagClipRectangle(x1=1.0, y1=2.0, x2=3.0, y2=4.0, inverse=False),
            r"{\clip(1,2,3,4)}",
        ),
        (
            AssTagClipRectangle(x1=1.0, y1=2.0, x2=3.0, y2=4.0, inverse=True),
            r"{\iclip(1,2,3,4)}",
        ),
        (
            AssTagClipRectangle(x1=1.1, y1=2.2, x2=3.3, y2=4.4, inverse=False),
            r"{\clip(1.1,2.2,3.3,4.4)}",
        ),
        (
            AssTagClipRectangle(x1=1.1, y1=2.2, x2=3.3, y2=4.4, inverse=True),
            r"{\iclip(1.1,2.2,3.3,4.4)}",
        ),
        (
            AssTagClipRectangle(x1=1, y1=2, x2=3, y2=4, inverse=False),
            r"{\clip(1,2,3,4)}",
        ),
        (
            AssTagClipRectangle(x1=1, y1=2, x2=3, y2=4, inverse=True),
            r"{\iclip(1,2,3,4)}",
        ),
        (
            AssTagClipVector(
                scale=1,
                path=[AssDrawCmdMove(AssDrawPoint(50, 0), close=True)],
                inverse=False,
            ),
            r"{\clip(1,m 50 0)}",
        ),
        (
            AssTagClipVector(
                scale=1,
                path=[AssDrawCmdMove(AssDrawPoint(50, 0), close=True)],
                inverse=True,
            ),
            r"{\iclip(1,m 50 0)}",
        ),
        (
            AssTagClipVector(
                scale=None,
                path=[AssDrawCmdMove(AssDrawPoint(50, 0), close=True)],
                inverse=False,
            ),
            r"{\clip(m 50 0)}",
        ),
        (
            AssTagClipVector(
                scale=None,
                path=[AssDrawCmdMove(AssDrawPoint(50, 0), close=True)],
                inverse=True,
            ),
            r"{\iclip(m 50 0)}",
        ),
    ],
)
def test_composing_valid_single_tag(
    source_tag: AssTag, expected_line: str
) -> None:
    assert expected_line == compose_ass([source_tag])